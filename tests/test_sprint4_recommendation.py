"""Prioridade das recomendações sujeitas à revisão humana."""

from __future__ import annotations

import unittest

from tests.sprint4_notebook_support import load_sprint4_namespace


class Sprint4RecommendationTest(unittest.TestCase):
    def test_prioritizes_retention_for_high_churn(self):
        _, namespace = load_sprint4_namespace()
        transcript = (
            "Usamos Protheus, mas não vamos renovar e vamos cancelar. "
            "Precisamos avaliar uma proposta antes da decisão final."
        )

        result = namespace["analisar_transcricao"](transcript, modo="fallback")

        self.assertEqual(result["risco_churn"]["label"], "alto")
        self.assertEqual(
            result["recomendacao_acao"]["label"], "acionar_retencao"
        )
        self.assertTrue(result["recomendacao_acao"]["revisao_humana"])

    def test_requires_manual_review_for_mixed_signals(self):
        _, namespace = load_sprint4_namespace()
        transcript = (
            "Gostei da solução, mas estou insatisfeito com o problema. "
            "Precisamos avaliar uma proposta para o Protheus."
        )

        result = namespace["analisar_transcricao"](transcript, modo="fallback")

        self.assertEqual(result["sentimento"]["label"], "misto")
        self.assertEqual(
            result["recomendacao_acao"]["label"], "revisar_manualmente"
        )
        self.assertEqual(
            result["recomendacao_acao"]["criterios"], ["sentimento_misto"]
        )

    def test_schedules_demo_for_opportunity_with_explicit_product(self):
        _, namespace = load_sprint4_namespace()
        transcript = (
            "Usamos Protheus e precisamos avaliar uma proposta para implantar um ERP."
        )

        result = namespace["analisar_transcricao"](transcript, modo="fallback")

        self.assertEqual(result["oportunidade_comercial"]["label"], "detectada")
        self.assertEqual(
            result["recomendacao_acao"]["label"], "agendar_demonstracao"
        )

    def test_qualifies_opportunity_without_explicit_product(self):
        _, namespace = load_sprint4_namespace()
        transcript = (
            "Temos retrabalho manual e precisamos avaliar uma proposta para "
            "implantar um software."
        )

        result = namespace["analisar_transcricao"](transcript, modo="fallback")

        self.assertEqual(result["oportunidade_comercial"]["label"], "detectada")
        self.assertEqual(
            result["recomendacao_acao"]["label"], "qualificar_oportunidade"
        )
        self.assertTrue(result["recomendacao_acao"]["revisao_humana"])
        self.assertEqual(
            result["recomendacao_acao"]["criterios"],
            ["oportunidade_detectada", "produto_sem_fundamentacao_suficiente"],
        )

    def test_public_result_explains_retention_from_high_churn(self):
        _, namespace = load_sprint4_namespace()
        result = namespace["analisar_transcricao"](
            "Usamos Protheus, mas não vamos renovar e vamos cancelar.",
            modo="fallback",
        )

        recommendation = result["recomendacao_acao"]
        self.assertEqual(recommendation["label"], "acionar_retencao")
        self.assertEqual(recommendation["criterios"], ["risco_churn_alto"])
        self.assertIn("churn", recommendation["motivo"].lower())

    def test_public_result_explains_demo_with_grounded_product(self):
        _, namespace = load_sprint4_namespace()
        result = namespace["analisar_transcricao"](
            "Usamos Protheus e precisamos avaliar uma proposta para implantar um ERP.",
            modo="fallback",
        )

        recommendation = result["recomendacao_acao"]
        self.assertEqual(recommendation["label"], "agendar_demonstracao")
        self.assertEqual(
            recommendation["criterios"],
            ["oportunidade_detectada", "produto_explicito_com_fonte"],
        )
        self.assertIn("produto", recommendation["motivo"].lower())

    def test_public_result_explains_follow_up_without_opportunity(self):
        _, namespace = load_sprint4_namespace()
        result = namespace["analisar_transcricao"](
            "Reunião de alinhamento da equipe na terça-feira.", modo="fallback"
        )

        recommendation = result["recomendacao_acao"]
        self.assertEqual(recommendation["label"], "acompanhar_conta")
        self.assertEqual(
            recommendation["criterios"], ["oportunidade_nao_detectada"]
        )
        self.assertTrue(recommendation["motivo"])

    def test_requires_manual_review_for_any_low_model_confidence(self):
        _, namespace = load_sprint4_namespace()
        sentiment = {
            "label": "neutro",
            "score": 0.40,
            "score_type": "model_probability",
        }
        churn = {
            "label": "baixo",
            "score": 0.90,
            "score_type": "model_probability",
        }
        opportunity = {
            "label": "nao_detectada",
            "score": 0.90,
            "score_type": "model_probability",
        }

        recommendation = namespace["_recommend_action"](
            [], sentiment, churn, opportunity
        )

        self.assertEqual(recommendation["label"], "revisar_manualmente")
        self.assertEqual(recommendation["criterios"], ["baixa_confianca"])

    def test_requires_manual_review_for_low_product_confidence(self):
        _, namespace = load_sprint4_namespace()
        products = [{"score": 0.60}]
        sentiment = {"label": "neutro", "score": 0.0, "score_type": "heuristic"}
        churn = {"label": "baixo", "score": 0.0, "score_type": "heuristic"}
        opportunity = {
            "label": "detectada",
            "score": 0.90,
            "score_type": "model_probability",
        }

        recommendation = namespace["_recommend_action"](
            products, sentiment, churn, opportunity
        )

        self.assertEqual(recommendation["label"], "revisar_manualmente")


if __name__ == "__main__":
    unittest.main()
