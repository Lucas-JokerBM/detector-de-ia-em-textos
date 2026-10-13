"""Contrato dos analisadores (Strategy + Registry): novos indicadores = nova classe, sem tocar no motor."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar

from detector_ia.core.document import AnalysisDocument
from detector_ia.core.lexicon import DEFAULT_LEXICON, Lexicon
from detector_ia.core.models import Metric


@dataclass(frozen=True)
class FlagHit:
    sentence: int  # índice em AnalysisDocument.sentences
    reason: str
    suggestion: str


@dataclass
class AnalyzerOutput:
    metric: Metric | None = None
    hits: list[FlagHit] = field(default_factory=list)


class Analyzer(ABC):
    id: ClassVar[str]
    name: ClassVar[str]
    default_weight: ClassVar[float] = 0.0

    def __init__(self, lexicon: Lexicon = DEFAULT_LEXICON) -> None:
        self.lexicon = lexicon

    @abstractmethod
    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput: ...

    def metric(self, value: str, score: float, explanation: str, advice: str = "") -> Metric:
        return Metric(self.id, self.name, value, round(score, 4), self.default_weight, explanation, advice)


_REGISTRY: dict[str, type[Analyzer]] = {}


def register(cls: type[Analyzer]) -> type[Analyzer]:
    if cls.id in _REGISTRY:
        raise ValueError(f"Analisador duplicado: {cls.id}")
    _REGISTRY[cls.id] = cls
    return cls


def default_analyzers(lexicon: Lexicon = DEFAULT_LEXICON) -> list[Analyzer]:
    return [cls(lexicon) for cls in _REGISTRY.values()]
