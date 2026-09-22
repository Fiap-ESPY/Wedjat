"""Comportamento público da análise comercial."""

import unittest

from wedjat import CommercialAnalysisService


class CommercialAnalysisServiceTest(unittest.TestCase):
    def test_analysis_preserves_transcript_and_returns_the_complete_contract(self):
        transcript = "Cliente relatou o cenário atual e pediu acompanhamento."

        result = CommercialAnalysisService().analyze(transcript).to_dict()

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
        self.assertEqual(result["analysis_mode"]["requested"], "auto")
        self.assertEqual(
            result["analysis_mode"]["components"],
            {
                "products": "fallback",
                "sentiment": "fallback",
                "churn": "fallback",
                "opportunity": "fallback",
            },
        )

        for indicator_name in (
            "sentimento",
            "risco_churn",
            "oportunidade_comercial",
        ):
            with self.subTest(indicator=indicator_name):
                indicator = result[indicator_name]
                self.assertEqual(indicator["score_type"], "heuristic")
                self.assertEqual(indicator["engine"], "fallback")
                self.assertIsNone(indicator["model"])

    def test_empty_transcript_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "transcrição não pode estar vazia"):
            CommercialAnalysisService().analyze("  \n\t")


if __name__ == "__main__":
    unittest.main()
