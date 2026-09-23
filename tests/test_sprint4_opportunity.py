"""Detecção de oportunidade comercial com BERTimbau e fallback."""

from __future__ import annotations

import unittest

from tests.sprint4_notebook_support import load_sprint4_namespace


class Sprint4OpportunityTest(unittest.TestCase):
    def test_uses_finetuned_bertimbau_when_available(self):
        _, namespace = load_sprint4_namespace()

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

    def test_fallback_requires_commercial_intent(self):
        _, namespace = load_sprint4_namespace()

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


if __name__ == "__main__":
    unittest.main()
