"""Identificação de produtos e extração de termos principais."""

from __future__ import annotations

import unittest

from tests.sprint4_notebook_support import load_sprint4_namespace


class Sprint4ProductsAndTermsTest(unittest.TestCase):
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
