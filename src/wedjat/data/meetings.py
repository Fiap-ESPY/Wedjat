"""Prepara as reuniões do Wedjat para as próximas etapas de NLP.

O módulo mantém uma reunião por registro e faz somente transformações
conservadoras. Limpeza linguística, tokenização e chunking pertencem a etapas
posteriores, pois precisam usar exatamente o tokenizer do modelo escolhido.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator, Sequence


# Reconhece o marcador anonimizado que inicia uma fala na transcrição.
SPEAKER_TURN_PATTERN = re.compile(r"\[LOCUTOR\s+\d+\]:")


class DataPreparationError(ValueError):
    """Indica que os dados não atendem ao contrato esperado pelo pipeline."""


@dataclass(frozen=True)
class PreparationSummary:
    """Contagens seguras para auditar o tratamento sem expor transcrições."""

    input_records: int
    output_meetings: int
    exact_duplicates_removed: int
    total_transcript_characters: int
    total_speaker_turns: int
    shortest_transcript_characters: int
    longest_transcript_characters: int


def iter_ndjson(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    """Lê um objeto JSON por linha e informa a linha de origem.

    A leitura é feita em streaming para que o consumo de memória não cresça com
    o volume total das transcrições.
    """

    with path.open("r", encoding="utf-8") as source:
        for line_number, raw_line in enumerate(source, start=1):
            # Linhas vazias são ignoradas porque não representam uma reunião.
            if not raw_line.strip():
                continue

            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                # O erro informa somente a posição, nunca o texto sensível.
                raise DataPreparationError(
                    f"JSON inválido na linha {line_number}: coluna {exc.colno}."
                ) from exc

            if not isinstance(record, dict):
                raise DataPreparationError(
                    f"A linha {line_number} deve conter um objeto JSON."
                )

            yield line_number, record


def normalize_transcript(text: str) -> str:
    """Normaliza formatação sem remover palavras, pontuação ou stopwords."""

    # Unifica quebras de linha produzidas por Windows, Linux ou sistemas legados.
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    cleaned_lines: list[str] = []
    for line in normalized.split("\n"):
        # Remove espaços nas bordas e repetições de espaço/tab dentro da linha.
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)

    return "\n".join(cleaned_lines)


def validate_and_enrich_record(
    record: dict[str, Any],
    line_number: int,
    required_fields: Sequence[str],
) -> dict[str, Any]:
    """Valida o contrato mínimo e acrescenta metadados úteis de tamanho."""

    for field_name in required_fields:
        if field_name not in record or record[field_name] in (None, ""):
            raise DataPreparationError(
                f"Campo obrigatório {field_name!r} ausente na linha {line_number}."
            )

    meeting_id = str(record["ID_MEETING"]).strip()
    transcript = record["ANON_TRANSCRICAO"]

    if not meeting_id:
        raise DataPreparationError(
            f"ID_MEETING vazio na linha {line_number}."
        )
    if not isinstance(transcript, str):
        raise DataPreparationError(
            f"ANON_TRANSCRICAO deve ser texto na linha {line_number}."
        )

    normalized_transcript = normalize_transcript(transcript)
    if not normalized_transcript:
        raise DataPreparationError(
            f"ANON_TRANSCRICAO vazia após normalização na linha {line_number}."
        )

    # A cópia preserva todos os metadados originais e evita alterar o objeto lido.
    prepared = dict(record)
    prepared["ID_MEETING"] = meeting_id
    prepared["ANON_TRANSCRICAO"] = normalized_transcript
    prepared["NUM_CARACTERES_TRANSCRICAO"] = len(normalized_transcript)
    prepared["NUM_TURNOS_TRANSCRICAO"] = len(
        SPEAKER_TURN_PATTERN.findall(normalized_transcript)
    )
    return prepared


def record_fingerprint(record: dict[str, Any]) -> str:
    """Cria uma assinatura estável para distinguir duplicata de conflito."""

    canonical_record = json.dumps(
        record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_record.encode("utf-8")).hexdigest()


def prepare_meetings(
    input_path: Path,
    output_path: Path,
    report_path: Path,
    required_fields: Sequence[str],
) -> PreparationSummary:
    """Valida, normaliza e deduplica reuniões, gerando dados e auditoria."""

    if not input_path.is_file():
        raise DataPreparationError(f"Arquivo de entrada não encontrado: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # O dicionário guarda só hashes, evitando manter transcrições inteiras na memória.
    fingerprints_by_meeting: dict[str, str] = {}
    input_records = 0
    output_meetings = 0
    exact_duplicates_removed = 0
    total_characters = 0
    total_turns = 0
    shortest_transcript: int | None = None
    longest_transcript = 0

    # Um arquivo temporário impede que uma falha deixe uma saída parcial válida.
    temporary_handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temporary_path = Path(temporary_handle.name)

    try:
        with temporary_handle as destination:
            for line_number, source_record in iter_ndjson(input_path):
                input_records += 1
                prepared = validate_and_enrich_record(
                    source_record,
                    line_number,
                    required_fields,
                )

                meeting_id = prepared["ID_MEETING"]
                fingerprint = record_fingerprint(prepared)
                previous_fingerprint = fingerprints_by_meeting.get(meeting_id)

                if previous_fingerprint is not None:
                    if previous_fingerprint == fingerprint:
                        exact_duplicates_removed += 1
                        continue
                    raise DataPreparationError(
                        "O mesmo ID_MEETING possui registros diferentes: "
                        f"conflito detectado na linha {line_number}."
                    )

                fingerprints_by_meeting[meeting_id] = fingerprint
                destination.write(json.dumps(prepared, ensure_ascii=False) + "\n")

                transcript_characters = prepared["NUM_CARACTERES_TRANSCRICAO"]
                output_meetings += 1
                total_characters += transcript_characters
                total_turns += prepared["NUM_TURNOS_TRANSCRICAO"]
                shortest_transcript = (
                    transcript_characters
                    if shortest_transcript is None
                    else min(shortest_transcript, transcript_characters)
                )
                longest_transcript = max(longest_transcript, transcript_characters)

        # A substituição só ocorre depois que toda a entrada foi validada.
        os.replace(temporary_path, output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    summary = PreparationSummary(
        input_records=input_records,
        output_meetings=output_meetings,
        exact_duplicates_removed=exact_duplicates_removed,
        total_transcript_characters=total_characters,
        total_speaker_turns=total_turns,
        shortest_transcript_characters=shortest_transcript or 0,
        longest_transcript_characters=longest_transcript,
    )
    write_json_atomic(report_path, asdict(summary))
    return summary


def write_json_atomic(path: Path, content: dict[str, Any]) -> None:
    """Grava um JSON primeiro em arquivo temporário e depois o publica."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary_handle:
        json.dump(content, temporary_handle, ensure_ascii=False, indent=2)
        temporary_handle.write("\n")
        temporary_path = Path(temporary_handle.name)

    os.replace(temporary_path, path)


def load_config(config_path: Path) -> tuple[Path, Path, Path, list[str]]:
    """Carrega a configuração e resolve caminhos relativos à raiz do projeto."""

    with config_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    # Como o arquivo fica em <raiz>/configs, o pai do diretório é a raiz.
    project_root = config_path.resolve().parent.parent

    def project_path(config_key: str) -> Path:
        configured_path = Path(config[config_key])
        return (
            configured_path
            if configured_path.is_absolute()
            else project_root / configured_path
        )

    required_fields = config.get(
        "required_fields",
        ["ID_MEETING", "ANON_TRANSCRICAO"],
    )
    if not isinstance(required_fields, list) or not all(
        isinstance(field, str) for field in required_fields
    ):
        raise DataPreparationError("required_fields deve ser uma lista de textos.")

    return (
        project_path("input_path"),
        project_path("output_path"),
        project_path("report_path"),
        required_fields,
    )


def main() -> None:
    """Executa o tratamento usando o arquivo de configuração informado."""

    parser = argparse.ArgumentParser(
        description="Prepara as reuniões do Wedjat sem expor as transcrições."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/data_preparation.json"),
        help="Caminho do arquivo JSON de configuração.",
    )
    arguments = parser.parse_args()

    input_path, output_path, report_path, required_fields = load_config(
        arguments.config
    )
    summary = prepare_meetings(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
        required_fields=required_fields,
    )

    # Apenas contagens são exibidas; nenhum trecho da reunião vai para o terminal.
    print(json.dumps(asdict(summary), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

