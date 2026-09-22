"""Contrato executável do notebook da Sprint 4."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "12_sprint4_commercial_analysis.ipynb"


def load_notebook_namespace() -> tuple[dict, dict]:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    tagged_sources = [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
        and "wedjat-core" in cell.get("metadata", {}).get("tags", [])
    ]
    if not tagged_sources:
        raise AssertionError("O notebook precisa de uma célula com a tag wedjat-core.")

    namespace = {
        "__name__": "wedjat_sprint4_notebook",
        "PROJECT_ROOT": ROOT,
    }
    exec("\n\n".join(tagged_sources), namespace)
    return notebook, namespace


class Sprint4NotebookTest(unittest.TestCase):
    def test_notebook_exposes_complete_analysis_contract(self):
        notebook, namespace = load_notebook_namespace()
        transcript = "Cliente relatou o cenário atual e pediu acompanhamento."

        result = namespace["analisar_transcricao"](transcript, modo="fallback")

        self.assertEqual(notebook["nbformat"], 4)
        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["transcricao_original"], transcript)
        self.assertIsNone(result["produto_identificado"])
        self.assertEqual(result["produtos_candidatos"], [])
        self.assertEqual(result["sentimento"]["label"], "neutro")
        self.assertEqual(result["risco_churn"]["label"], "baixo")
        self.assertEqual(result["oportunidade_comercial"]["label"], "nao_detectada")
        self.assertEqual(result["principais_termos"], [])
        self.assertEqual(result["recomendacao_acao"]["label"], "acompanhar_conta")
        self.assertTrue(result["recomendacao_acao"]["revisao_humana"])
        self.assertEqual(result["analysis_mode"]["requested"], "fallback")

    def test_notebook_rejects_an_empty_transcript(self):
        _, namespace = load_notebook_namespace()

        with self.assertRaisesRegex(ValueError, "transcrição não pode estar vazia"):
            namespace["analisar_transcricao"]("  \n\t", modo="fallback")


if __name__ == "__main__":
    unittest.main()
