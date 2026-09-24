"""Carregamento compartilhado dos módulos notebook-first da Sprint 4."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_FILES = (
    "12_fundamentos_analise.ipynb",
    "13_produtos_e_termos.ipynb",
    "14_analise_sentimento.ipynb",
    "15_risco_churn.ipynb",
    "16_oportunidade_comercial.ipynb",
    "17_recomendacao_acao.ipynb",
    "18_analise_comercial.ipynb",
)


def load_notebooks() -> list[dict]:
    return [
        json.loads((ROOT / "notebooks" / filename).read_text(encoding="utf-8"))
        for filename in NOTEBOOK_FILES
    ]


def load_sprint4_namespace() -> tuple[list[dict], dict]:
    notebooks = load_notebooks()
    tagged_sources = [
        "".join(cell["source"])
        for notebook in notebooks
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
        and "wedjat-core" in cell.get("metadata", {}).get("tags", [])
    ]
    if not tagged_sources:
        raise AssertionError("Os notebooks precisam de células com a tag wedjat-core.")

    namespace = {
        "__name__": "wedjat_sprint4_notebooks",
        "PROJECT_ROOT": ROOT,
    }
    exec("\n\n".join(tagged_sources), namespace)
    offline_error = RuntimeError("Modelos externos desabilitados nos testes determinísticos.")
    for variable in (
        "_E5_LOAD_ERROR",
        "_SENTIMENT_LOAD_ERROR",
        "_CHURN_LOAD_ERROR",
        "_OPPORTUNITY_LOAD_ERROR",
    ):
        namespace[variable] = offline_error
    return notebooks, namespace
