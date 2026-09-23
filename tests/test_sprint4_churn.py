"""Classificação do sinal de risco de churn."""

from __future__ import annotations

import unittest

from tests.sprint4_notebook_support import load_sprint4_namespace


class Sprint4ChurnTest(unittest.TestCase):
    def test_uses_minilm_zero_shot_when_available(self):
        _, namespace = load_sprint4_namespace()

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

    def test_fallback_detects_explicit_cancellation_risk(self):
        _, namespace = load_sprint4_namespace()

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

    def test_does_not_hide_churn_inference_errors(self):
        _, namespace = load_sprint4_namespace()

        class BrokenChurnClassifier:
            @staticmethod
            def __call__(_text, **_kwargs):
                raise RuntimeError("falha simulada de inferência")

        namespace["_CHURN_CLASSIFIER"] = BrokenChurnClassifier()

        with self.assertRaisesRegex(RuntimeError, "falha simulada"):
            namespace["analisar_transcricao"]("Atendimento normal.", modo="auto")


if __name__ == "__main__":
    unittest.main()
