"""Garante que o tratamento preserve reuniões e bloqueie dados ambíguos."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


# Permite importar o pacote diretamente da pasta src sem instalar o projeto.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from wedjat.data.meetings import (  # noqa: E402
    DataPreparationError,
    normalize_transcript,
    prepare_meetings,
)


class NormalizeTranscriptTests(unittest.TestCase):
    """Testa somente a limpeza conservadora do texto."""

    def test_normalizes_spacing_without_removing_words(self) -> None:
        source = "  [LOCUTOR 1]:  Olá\r\n\r\n Tudo\t bem.  "

        result = normalize_transcript(source)

        self.assertEqual(result, "[LOCUTOR 1]: Olá\nTudo bem.")


class PrepareMeetingsTests(unittest.TestCase):
    """Testa validação, enriquecimento e deduplicação por reunião."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temporary_directory.name)
        self.input_path = self.base_path / "input.jsonl"
        self.output_path = self.base_path / "processed" / "meetings.jsonl"
        self.report_path = self.base_path / "reports" / "summary.json"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_records(self, records: list[dict[str, object]]) -> None:
        """Cria uma entrada sintética; nenhum dado real aparece nos testes."""

        with self.input_path.open("w", encoding="utf-8") as destination:
            for record in records:
                destination.write(json.dumps(record, ensure_ascii=False) + "\n")

    def test_removes_exact_duplicates_and_adds_counts(self) -> None:
        first = {
            "ID_MEETING": "meeting-1",
            "ANON_TRANSCRICAO": "[LOCUTOR 1]:  Olá\n[LOCUTOR 2]: Oi",
        }
        second = {
            "ID_MEETING": "meeting-2",
            "ANON_TRANSCRICAO": "[LOCUTOR 3]: Exemplo sintético",
        }
        self.write_records([first, first, second])

        summary = prepare_meetings(
            self.input_path,
            self.output_path,
            self.report_path,
            ["ID_MEETING", "ANON_TRANSCRICAO"],
        )

        output_records = [
            json.loads(line)
            for line in self.output_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(summary.input_records, 3)
        self.assertEqual(summary.output_meetings, 2)
        self.assertEqual(summary.exact_duplicates_removed, 1)
        self.assertEqual(len(output_records), 2)
        self.assertEqual(output_records[0]["NUM_TURNOS_TRANSCRICAO"], 2)
        self.assertEqual(
            output_records[0]["NUM_CARACTERES_TRANSCRICAO"],
            len(output_records[0]["ANON_TRANSCRICAO"]),
        )
        self.assertTrue(self.report_path.is_file())

    def test_rejects_different_records_with_the_same_meeting_id(self) -> None:
        self.write_records(
            [
                {"ID_MEETING": "meeting-1", "ANON_TRANSCRICAO": "Versão A"},
                {"ID_MEETING": "meeting-1", "ANON_TRANSCRICAO": "Versão B"},
            ]
        )

        with self.assertRaisesRegex(DataPreparationError, "registros diferentes"):
            prepare_meetings(
                self.input_path,
                self.output_path,
                self.report_path,
                ["ID_MEETING", "ANON_TRANSCRICAO"],
            )

        # A saída definitiva não pode existir após uma preparação incompleta.
        self.assertFalse(self.output_path.exists())

    def test_rejects_missing_required_field(self) -> None:
        self.write_records([{"ID_MEETING": "meeting-1"}])

        with self.assertRaisesRegex(DataPreparationError, "ANON_TRANSCRICAO"):
            prepare_meetings(
                self.input_path,
                self.output_path,
                self.report_path,
                ["ID_MEETING", "ANON_TRANSCRICAO"],
            )


if __name__ == "__main__":
    unittest.main()

