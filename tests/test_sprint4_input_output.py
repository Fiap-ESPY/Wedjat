"""Entrada única e persistência opcional do notebook integrado."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tests.sprint4_notebook_support import load_sprint4_namespace


class Sprint4InputOutputTest(unittest.TestCase):
    def test_direct_text_is_preserved_without_normalization(self):
        _, namespace = load_sprint4_namespace()
        transcript = "  Linha original com acento.\nSegunda linha.  "

        loaded = namespace["carregar_transcricao"](texto=transcript)
        result = namespace["analisar_transcricao"](loaded, modo="fallback")

        self.assertEqual(loaded, transcript)
        self.assertEqual(result["transcricao_original"], transcript)

    def test_reads_one_transcript_from_txt_or_json(self):
        _, namespace = load_sprint4_namespace()
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            txt_transcript = "Texto do arquivo.\n"
            txt_path = temporary / "reuniao.txt"
            txt_path.write_bytes(txt_transcript.encode("utf-8"))
            json_transcript = "Texto exportado em JSON."
            json_path = temporary / "reuniao.json"
            json_path.write_text(
                json.dumps({"ANON_TRANSCRICAO": json_transcript}), encoding="utf-8"
            )

            loaded_txt = namespace["carregar_transcricao"](arquivo=txt_path)
            loaded_json = namespace["carregar_transcricao"](
                arquivo=json_path, campo_json="ANON_TRANSCRICAO"
            )

        self.assertEqual(loaded_txt, txt_transcript)
        self.assertEqual(loaded_json, json_transcript)

    def test_rejects_ambiguous_or_invalid_input(self):
        _, namespace = load_sprint4_namespace()
        load = namespace["carregar_transcricao"]

        with self.assertRaisesRegex(ValueError, "exatamente uma fonte"):
            load()
        with self.assertRaisesRegex(ValueError, "exatamente uma fonte"):
            load(texto="texto", arquivo="reuniao.txt")

        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            list_path = temporary / "lote.json"
            list_path.write_text('[{"transcricao": "uma"}]', encoding="utf-8")
            missing_path = temporary / "sem_campo.json"
            missing_path.write_text('{"id": 1}', encoding="utf-8")
            invalid_path = temporary / "invalido.json"
            invalid_path.write_text("{", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "objeto JSON"):
                load(arquivo=list_path)
            with self.assertRaisesRegex(ValueError, "campo 'transcricao'"):
                load(arquivo=missing_path)
            with self.assertRaisesRegex(ValueError, "JSON inválido"):
                load(arquivo=invalid_path)

    def test_writes_json_only_when_output_path_is_configured(self):
        _, namespace = load_sprint4_namespace()
        result = {"transcricao_original": "Texto", "sentimento": {"label": "neutro"}}

        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            self.assertIsNone(namespace["salvar_resultado"](result, None))
            self.assertEqual(list(temporary.iterdir()), [])

            output_path = temporary / "saida" / "analise.json"
            saved_path = namespace["salvar_resultado"](result, output_path)

            self.assertEqual(saved_path, output_path)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")), result
            )

    def test_runs_the_complete_single_transcript_flow(self):
        _, namespace = load_sprint4_namespace()
        transcript = "Usamos Protheus e precisamos avaliar uma proposta para o estoque."

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "analise.json"
            loaded = namespace["carregar_transcricao"](texto=transcript)
            result = namespace["analisar_transcricao"](loaded, modo="fallback")
            saved = namespace["salvar_resultado"](result, output_path)
            persisted = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(saved, output_path)
        self.assertEqual(persisted, result)
        self.assertEqual(result["transcricao_original"], transcript)
        self.assertIn("Protheus", result["produto_identificado"])
        self.assertEqual(result["oportunidade_comercial"]["label"], "detectada")
        self.assertTrue(result["recomendacao_acao"]["revisao_humana"])


if __name__ == "__main__":
    unittest.main()
