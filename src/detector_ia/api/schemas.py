"""Contrato público da API (versionado em /api/v1)."""
from __future__ import annotations

from pydantic import BaseModel


class MetricOut(BaseModel):
    id: str
    name: str
    value: str
    score: float
    weight: float
    explanation: str
    advice: str = ""


class FlagOut(BaseModel):
    id: int
    text: str
    reasons: list[str]
    suggestions: list[str]
    severity: int


class SegmentOut(BaseModel):
    text: str
    flag: int | None = None


class ParagraphOut(BaseModel):
    heading: bool
    segments: list[SegmentOut]


class AnalysisOut(BaseModel):
    engine_version: str
    score: float
    verdict: str
    words: int
    warnings: list[str]
    metrics: list[MetricOut]
    flags: list[FlagOut]
    global_advice: list[str]
    paragraphs: list[ParagraphOut]


class HealthOut(BaseModel):
    status: str
    version: str
