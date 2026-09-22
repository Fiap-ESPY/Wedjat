"""Fronteira pública da análise comercial do Wedjat."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class IndicatorResult:
    """Label e proveniência de um indicador comercial."""

    label: str
    score: float
    score_type: str
    engine: str
    model: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "score": self.score,
            "score_type": self.score_type,
            "engine": self.engine,
            "model": self.model,
        }


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    """Próximo passo que depende de revisão humana."""

    label: str
    revisao_humana: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "revisao_humana": self.revisao_humana,
        }


@dataclass(frozen=True, slots=True)
class CommercialAnalysis:
    """Resultado serializável da análise de uma transcrição."""

    transcricao_original: str
    produto_identificado: str | None
    produtos_candidatos: tuple[dict[str, Any], ...]
    sentimento: IndicatorResult
    risco_churn: IndicatorResult
    oportunidade_comercial: IndicatorResult
    principais_termos: tuple[str, ...]
    recomendacao_acao: RecommendationResult
    requested_mode: str
    component_modes: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "transcricao_original": self.transcricao_original,
            "produto_identificado": self.produto_identificado,
            "produtos_candidatos": [dict(item) for item in self.produtos_candidatos],
            "sentimento": self.sentimento.to_dict(),
            "risco_churn": self.risco_churn.to_dict(),
            "oportunidade_comercial": self.oportunidade_comercial.to_dict(),
            "principais_termos": list(self.principais_termos),
            "recomendacao_acao": self.recomendacao_acao.to_dict(),
            "analysis_mode": {
                "requested": self.requested_mode,
                "components": dict(self.component_modes),
            },
        }


class CommercialAnalysisService:
    """Analisa uma transcrição por vez por uma única interface pública."""

    _SUPPORTED_MODES = frozenset({"auto", "fallback", "full"})

    def __init__(self, mode: str = "auto") -> None:
        if mode not in self._SUPPORTED_MODES:
            supported = ", ".join(sorted(self._SUPPORTED_MODES))
            raise ValueError(f"Modo inválido: {mode!r}. Use um de: {supported}.")
        self._mode = mode

    def analyze(self, transcription: str) -> CommercialAnalysis:
        if not isinstance(transcription, str):
            raise TypeError("A transcrição deve ser uma string.")
        if not transcription.strip():
            raise ValueError("A transcrição não pode estar vazia.")

        return CommercialAnalysis(
            transcricao_original=transcription,
            produto_identificado=None,
            produtos_candidatos=(),
            sentimento=self._fallback_indicator("neutro"),
            risco_churn=self._fallback_indicator("baixo"),
            oportunidade_comercial=self._fallback_indicator("nao_detectada"),
            principais_termos=(),
            recomendacao_acao=RecommendationResult("acompanhar_conta"),
            requested_mode=self._mode,
            component_modes={
                "products": "fallback",
                "sentiment": "fallback",
                "churn": "fallback",
                "opportunity": "fallback",
            },
        )

    @staticmethod
    def _fallback_indicator(label: str) -> IndicatorResult:
        return IndicatorResult(
            label=label,
            score=0.0,
            score_type="heuristic",
            engine="fallback",
        )
