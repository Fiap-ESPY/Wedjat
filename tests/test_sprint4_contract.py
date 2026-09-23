"""Contrato público e organização dos notebooks da Sprint 4."""

from __future__ import annotations

import unittest

from tests.sprint4_notebook_support import NOTEBOOK_FILES, load_sprint4_namespace


class Sprint4ContractTest(unittest.TestCase):
    def test_notebooks_are_explanatory_modules_with_short_code_cells(self):
        notebooks, _ = load_sprint4_namespace()

        self.assertEqual(len(notebooks), len(NOTEBOOK_FILES))
        for filename, notebook in zip(NOTEBOOK_FILES, notebooks):
            self.assertEqual(notebook["nbformat"], 4, filename)
            markdown_cells = [
                cell for cell in notebook["cells"] if cell["cell_type"] == "markdown"
            ]
            code_cells = [
                cell for cell in notebook["cells"] if cell["cell_type"] == "code"
            ]
            self.assertGreaterEqual(len(markdown_cells), len(code_cells), filename)
            self.assertTrue(
                all(len("".join(cell["source"]).splitlines()) <= 90 for cell in code_cells),
                f"{filename} contém uma célula de código extensa.",
            )

    def test_integrated_notebook_exposes_complete_analysis_contract(self):
        _, namespace = load_sprint4_namespace()
        transcript = "Cliente relatou o cenário atual e pediu acompanhamento."

        result = namespace["analisar_transcricao"](transcript, modo="fallback")

        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["transcricao_original"], transcript)
        self.assertIsNone(result["produto_identificado"])
        self.assertEqual(result["produtos_candidatos"], [])
        self.assertEqual(result["produto_metadados"]["engine"], "bm25_aliases")
        self.assertEqual(result["produto_metadados"]["score_type"], "heuristic")
        self.assertEqual(
            result["produto_metadados"]["status"], "no_grounded_candidate"
        )
        self.assertEqual(result["sentimento"]["label"], "neutro")
        self.assertEqual(result["risco_churn"]["label"], "baixo")
        self.assertEqual(result["oportunidade_comercial"]["label"], "nao_detectada")
        self.assertIsInstance(result["principais_termos"], list)
        self.assertLessEqual(len(result["principais_termos"]), 10)
        self.assertEqual(result["recomendacao_acao"]["label"], "acompanhar_conta")
        self.assertTrue(result["recomendacao_acao"]["revisao_humana"])
        self.assertIn("model_probability", result["score_legend"])
        self.assertIn("heuristic", result["score_legend"])
        self.assertIn("normalized_cosine_similarity", result["score_legend"])
        self.assertEqual(result["analysis_mode"]["requested"], "fallback")

    def test_auto_mode_reports_safe_structured_fallback_reasons(self):
        _, namespace = load_sprint4_namespace()

        result = namespace["analisar_transcricao"](
            "Cliente pediu acompanhamento.", modo="auto"
        )

        reasons = result["analysis_mode"]["fallback_reasons"]
        self.assertEqual(reasons["products"]["code"], "model_load_failed")
        self.assertEqual(reasons["products"]["error_type"], "RuntimeError")
        self.assertNotIn("message", reasons["products"])

    def test_integrated_notebook_rejects_an_empty_transcript(self):
        _, namespace = load_sprint4_namespace()

        with self.assertRaisesRegex(ValueError, "transcrição não pode estar vazia"):
            namespace["analisar_transcricao"]("  \n\t", modo="fallback")


if __name__ == "__main__":
    unittest.main()
