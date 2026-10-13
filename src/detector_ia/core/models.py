"""Modelos de dados imutáveis/serializáveis usados por todo o sistema."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Paragraph:
    text: str
    style: str = ""
    is_heading: bool = False


@dataclass(frozen=True)
class Sentence:
    paragraph: int
    start: int
    end: int
    text: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class Metric:
    id: str
    name: str
    value: str
    score: float  # 0 = típico de humano .. 1 = típico de I.A.
    weight: float
    explanation: str
    advice: str = ""


@dataclass(frozen=True)
class Segment:
    text: str
    flag: int | None = None  # id do Flag, se o trecho foi sinalizado


@dataclass(frozen=True)
class ParagraphView:
    heading: bool
    segments: list[Segment]


@dataclass(frozen=True)
class Flag:
    id: int
    text: str
    reasons: list[str]
    suggestions: list[str]
    severity: int


@dataclass
class AnalysisResult:
    engine_version: str
    score: float
    verdict: str
    words: int
    warnings: list[str] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    flags: list[Flag] = field(default_factory=list)
    global_advice: list[str] = field(default_factory=list)
    paragraphs: list[ParagraphView] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
