"""Análise de sentimento com modelo e fallback."""

from __future__ import annotations

from types import SimpleNamespace
import unittest

from tests.sprint4_notebook_support import load_sprint4_namespace


class Sprint4SentimentTest(unittest.TestCase):
    def test_uses_pysentimiento_when_model_is_available(self):
        _, namespace = load_sprint4_namespace()

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

    def test_fallback_preserves_mixed_signals(self):
        _, namespace = load_sprint4_namespace()

        result = namespace["analisar_transcricao"](
            "Gostei muito da solução, mas estamos insatisfeitos e pensando em cancelar.",
            modo="fallback",
        )

        self.assertEqual(result["sentimento"]["label"], "misto")
        self.assertGreater(result["sentimento"]["score"], 0.0)
        self.assertEqual(result["sentimento"]["score_type"], "heuristic")
        self.assertEqual(result["sentimento"]["engine"], "lexical_sentiment")
        self.assertIsNone(result["sentimento"]["model"])

    def test_does_not_hide_sentiment_inference_errors(self):
        _, namespace = load_sprint4_namespace()

        class BrokenSentimentAnalyzer:
            @staticmethod
            def predict(_text):
                raise RuntimeError("falha simulada de inferência")

        namespace["_SENTIMENT_ANALYZER"] = BrokenSentimentAnalyzer()

        with self.assertRaisesRegex(RuntimeError, "falha simulada"):
            namespace["analisar_transcricao"]("Atendimento normal.", modo="auto")


if __name__ == "__main__":
    unittest.main()
