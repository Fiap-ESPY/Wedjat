"""Identificação de produtos e extração de termos principais."""

from __future__ import annotations

import unittest

from tests.sprint4_notebook_support import load_sprint4_namespace


class Sprint4ProductsAndTermsTest(unittest.TestCase):
    def test_uses_e5_ranking_when_local_artifacts_are_available(self):
        _, namespace = load_sprint4_namespace()

        class E5Retriever:
            @staticmethod
            def __call__(_text, top_k=3):
                self.assertEqual(top_k, 3)
                return [
                    {
                        "product": "TOTVS Protheus",
                        "score": 0.88,
                        "score_type": "normalized_cosine_similarity",
                        "engine": "multilingual_e5_small",
                        "model": "intfloat/multilingual-e5-small",
                        "explicit_match": True,
                        "matched_terms": ["protheus", "estoque"],
                        "document_ids": ["produto_protheus"],
                        "sources": ["https://www.totvs.com/protheus/"],
                    }
                ]

        namespace["_E5_RETRIEVER"] = E5Retriever()

        result = namespace["analisar_transcricao"](
            "Usamos Protheus e precisamos integrar o estoque.", modo="auto"
        )

        candidate = result["produtos_candidatos"][0]
        self.assertEqual(candidate["engine"], "multilingual_e5_small")
        self.assertEqual(candidate["score_type"], "normalized_cosine_similarity")
        self.assertEqual(candidate["score"], 0.88)
        self.assertEqual(result["analysis_mode"]["components"]["products"], "model")

    def test_ranks_grounded_totvs_products(self):
        _, namespace = load_sprint4_namespace()
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
        self.assertTrue(top_candidate["explicit_match"])
        self.assertIn("protheus", top_candidate["matched_terms"])
        self.assertTrue(top_candidate["document_ids"])
        self.assertTrue(top_candidate["sources"])
        self.assertNotIn("content", top_candidate)

    def test_extracts_prioritized_terms_without_personal_data(self):
        _, namespace = load_sprint4_namespace()
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
