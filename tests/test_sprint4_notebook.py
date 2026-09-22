"""Contrato executável do notebook da Sprint 4."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
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

    def test_notebook_ranks_grounded_totvs_products(self):
        _, namespace = load_notebook_namespace()
        transcript = (
            "Usamos Protheus no financeiro, mas precisamos melhorar estoque, "
            "compras e faturamento."
        )

        result = namespace["analisar_transcricao"](transcript, modo="fallback")

        self.assertIn("Protheus", result["produto_identificado"])
        self.assertGreaterEqual(len(result["produtos_candidatos"]), 1)
        self.assertLessEqual(len(result["produtos_candidatos"]), 3)
        top_candidate = result["produtos_candidatos"][0]
        self.assertEqual(top_candidate["product"], result["produto_identificado"])
        self.assertEqual(top_candidate["score_type"], "heuristic")
        self.assertEqual(top_candidate["engine"], "bm25_aliases")
        self.assertIn("protheus", top_candidate["matched_terms"])
        self.assertTrue(top_candidate["document_ids"])
        self.assertTrue(top_candidate["sources"])
        self.assertNotIn("content", top_candidate)

    def test_notebook_uses_pysentimiento_when_the_model_is_available(self):
        _, namespace = load_notebook_namespace()

        class PositiveSentimentAnalyzer:
            @staticmethod
            def predict(_text):
                return SimpleNamespace(
                    probas={"POS": 0.91, "NEG": 0.03, "NEU": 0.06}
                )

        namespace["_SENTIMENT_ANALYZER"] = PositiveSentimentAnalyzer()

        result = namespace["analisar_transcricao"](
            "A conversa foi ótima e a equipe ficou satisfeita.", modo="auto"
        )

        self.assertEqual(result["sentimento"]["label"], "positivo")
        self.assertEqual(result["sentimento"]["score"], 0.91)
        self.assertEqual(result["sentimento"]["score_type"], "model_probability")
        self.assertEqual(result["sentimento"]["engine"], "pysentimiento")
        self.assertEqual(
            result["sentimento"]["model"], "pysentimiento/bertweet-pt-sentiment"
        )
        self.assertEqual(result["analysis_mode"]["components"]["sentiment"], "model")

    def test_notebook_sentiment_fallback_preserves_mixed_signals(self):
        _, namespace = load_notebook_namespace()

        result = namespace["analisar_transcricao"](
            "Gostei muito da solução, mas estamos insatisfeitos e pensando em cancelar.",
            modo="fallback",
        )

        self.assertEqual(result["sentimento"]["label"], "misto")
        self.assertGreater(result["sentimento"]["score"], 0.0)
        self.assertEqual(result["sentimento"]["score_type"], "heuristic")
        self.assertEqual(result["sentimento"]["engine"], "lexical_sentiment")
        self.assertIsNone(result["sentimento"]["model"])


if __name__ == "__main__":
    unittest.main()
