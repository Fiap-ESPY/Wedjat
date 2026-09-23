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
        self.assertIsInstance(result["principais_termos"], list)
        self.assertLessEqual(len(result["principais_termos"]), 10)
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

    def test_notebook_uses_minilm_zero_shot_for_churn_when_available(self):
        _, namespace = load_notebook_namespace()

        class HighChurnClassifier:
            @staticmethod
            def __call__(_text, candidate_labels, **_kwargs):
                descriptions = namespace["CHURN_HYPOTHESES"]
                return {
                    "labels": [
                        descriptions["alto"],
                        descriptions["medio"],
                        descriptions["baixo"],
                    ],
                    "scores": [0.82, 0.12, 0.06],
                }

        namespace["_CHURN_CLASSIFIER"] = HighChurnClassifier()

        result = namespace["analisar_transcricao"](
            "Estamos avaliando encerrar o contrato no próximo trimestre.", modo="auto"
        )

        self.assertEqual(result["risco_churn"]["label"], "alto")
        self.assertEqual(result["risco_churn"]["score"], 0.82)
        self.assertEqual(result["risco_churn"]["score_type"], "model_probability")
        self.assertEqual(result["risco_churn"]["engine"], "zero_shot_nli")
        self.assertEqual(
            result["risco_churn"]["model"],
            "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli",
        )
        self.assertEqual(result["analysis_mode"]["components"]["churn"], "model")

    def test_notebook_churn_fallback_detects_explicit_cancellation_risk(self):
        _, namespace = load_notebook_namespace()

        result = namespace["analisar_transcricao"](
            "Não vamos renovar o contrato. Se o problema continuar, vamos cancelar "
            "e migrar para um concorrente.",
            modo="fallback",
        )

        self.assertEqual(result["risco_churn"]["label"], "alto")
        self.assertGreater(result["risco_churn"]["score"], 0.5)
        self.assertEqual(result["risco_churn"]["score_type"], "heuristic")
        self.assertEqual(result["risco_churn"]["engine"], "lexical_churn")
        self.assertIsNone(result["risco_churn"]["model"])

    def test_notebook_uses_finetuned_bertimbau_for_opportunity_when_available(self):
        _, namespace = load_notebook_namespace()

        class OpportunityClassifier:
            @staticmethod
            def __call__(_text, **_kwargs):
                return [
                    {"label": "nao_oportunidade", "score": 0.08},
                    {"label": "oportunidade", "score": 0.92},
                ]

        namespace["_OPPORTUNITY_CLASSIFIER"] = OpportunityClassifier()

        result = namespace["analisar_transcricao"](
            "Precisamos automatizar o estoque e queremos avaliar uma proposta.",
            modo="auto",
        )

        opportunity = result["oportunidade_comercial"]
        self.assertEqual(opportunity["label"], "detectada")
        self.assertEqual(opportunity["score"], 0.92)
        self.assertEqual(opportunity["score_type"], "model_probability")
        self.assertEqual(opportunity["engine"], "bertimbau_finetuned")
        self.assertEqual(
            opportunity["model"], "data/processed/bertimbau_opportunity_best"
        )
        self.assertEqual(result["analysis_mode"]["components"]["opportunity"], "model")

    def test_notebook_opportunity_fallback_requires_commercial_intent(self):
        _, namespace = load_notebook_namespace()

        detected = namespace["analisar_transcricao"](
            "Temos retrabalho manual e precisamos avaliar uma proposta para implantar um ERP.",
            modo="fallback",
        )
        absent = namespace["analisar_transcricao"](
            "A equipe comentou o funcionamento atual do ERP.", modo="fallback"
        )

        self.assertEqual(detected["oportunidade_comercial"]["label"], "detectada")
        self.assertGreater(detected["oportunidade_comercial"]["score"], 0.0)
        self.assertEqual(
            detected["oportunidade_comercial"]["score_type"], "heuristic"
        )
        self.assertEqual(
            detected["oportunidade_comercial"]["engine"], "lexical_opportunity"
        )
        self.assertIsNone(detected["oportunidade_comercial"]["model"])
        self.assertEqual(absent["oportunidade_comercial"]["label"], "nao_detectada")

    def test_notebook_extracts_prioritized_key_terms_without_personal_data(self):
        _, namespace = load_notebook_namespace()
        transcript = (
            "Usamos Protheus, mas as planilhas geram retrabalho manual. "
            "Estamos avaliando Oracle e precisamos de uma proposta de integração. "
            "Contato: maria.silva@example.com, telefone (11) 99876-5432."
        )

        result = namespace["analisar_transcricao"](transcript, modo="fallback")
        terms = result["principais_termos"]
        normalized_terms = [namespace["_normalize"](term) for term in terms]

        self.assertLessEqual(len(terms), 10)
        self.assertEqual(len(terms), len(set(normalized_terms)))
        self.assertTrue(any("protheus" in term for term in normalized_terms))
        self.assertIn("retrabalho", normalized_terms)
        self.assertIn("oracle", normalized_terms)
        self.assertIn("proposta", normalized_terms)
        self.assertNotIn("maria", normalized_terms)
        self.assertFalse(any("99876" in term for term in normalized_terms))


if __name__ == "__main__":
    unittest.main()
