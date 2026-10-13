"""Funções puras de processamento de texto e estatística."""
from __future__ import annotations

import re
import statistics
from collections.abc import Sequence

TOKEN_RE = re.compile(r"[\wÀ-ÿ'’-]+", re.UNICODE)
SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[\"“(]?[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9])")


def tokens(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def split_sentences(text: str) -> list[tuple[int, int]]:
    """Retorna (início, fim) de cada frase dentro do parágrafo."""
    spans, start = [], 0
    for m in SENT_SPLIT.finditer(text):
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(text)))
    return [(s, e) for s, e in spans if text[s:e].strip()]


def ramp(x: float, lo: float, hi: float) -> float:
    """Normaliza x para [0, 1] (0 em lo, 1 em hi)."""
    if hi == lo:
        return 0.0
    return max(0.0, min(1.0, (x - lo) / (hi - lo)))


def coeff_variation(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = statistics.mean(values)
    return statistics.pstdev(values) / mean if mean else 0.0


def mattr(toks: Sequence[str], window: int = 50) -> float | None:
    """Moving-Average Type-Token Ratio; None se o texto for curto demais."""
    if len(toks) < window + 10:
        return None
    ratios = [len(set(toks[i:i + window])) / window for i in range(0, len(toks) - window + 1, 5)]
    return sum(ratios) / len(ratios)
