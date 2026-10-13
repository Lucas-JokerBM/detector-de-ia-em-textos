"""Motor de análise: orquestra analisadores, pondera o score e monta o resultado."""
from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import replace

import detector_ia.core.analyzers  # noqa: F401  (registra os analisadores padrão)
from detector_ia import __version__
from detector_ia.core.analyzers.base import Analyzer, FlagHit, default_analyzers
from detector_ia.core.document import AnalysisDocument
from detector_ia.core.lexicon import DEFAULT_LEXICON, Lexicon
from detector_ia.core.models import (
    AnalysisResult,
    Flag,
    Metric,
    Paragraph,
    ParagraphView,
    Segment,
)

log = logging.getLogger(__name__)

VERDICTS = (
    (30, "Provavelmente escrito por humano"),
    (50, "Indícios mistos (pode ter partes assistidas por I.A.)"),
    (70, "Indícios fortes de texto gerado/assistido por I.A."),
    (101, "Muito provável texto gerado por I.A."),
)


def verdict_for(score: float) -> str:
    return next(label for limit, label in VERDICTS if score < limit)


class AnalysisEngine:
    """Sem estado entre chamadas: pode ser compartilhado entre threads e processos."""

    def __init__(
        self,
        analyzers: Sequence[Analyzer] | None = None,
        weights: Mapping[str, float] | None = None,
        lexicon: Lexicon = DEFAULT_LEXICON,
    ) -> None:
        self.analyzers = list(analyzers) if analyzers is not None else default_analyzers(lexicon)
        self.weights = dict(weights or {})

    def analyze(self, paragraphs: Sequence[Paragraph]) -> AnalysisResult:
        doc = AnalysisDocument(paragraphs)
        views = [ParagraphView(p.is_heading, [Segment(p.text)]) for p in doc.paragraphs]
        if not doc.sentences:
            return AnalysisResult(__version__, 0.0, "Texto insuficiente para análise", doc.word_count,
                                  ["Não há texto corrido suficiente no documento."], paragraphs=views)

        warnings = []
        if doc.word_count < 150:
            warnings.append("Texto curto (< 150 palavras): a confiança da análise é baixa.")
        elif doc.word_count < 400:
            warnings.append("Texto relativamente curto (< 400 palavras): resultado menos confiável.")

        metrics: list[Metric] = []
        hits: list[FlagHit] = []
        for analyzer in self.analyzers:
            try:  # um analisador defeituoso não derruba a análise inteira
                out = analyzer.analyze(doc)
            except Exception:  # noqa: BLE001
                log.exception("Falha no analisador %s", analyzer.id)
                continue
            if out.metric:
                weight = self.weights.get(analyzer.id, out.metric.weight)
                metrics.append(replace(out.metric, weight=weight))
            hits.extend(out.hits)

        weighted = [m for m in metrics if m.weight > 0]
        total = sum(m.weight for m in weighted)
        score = round(sum(m.score * m.weight for m in weighted) / total * 100, 1) if total else 0.0

        flags, flag_of = self._build_flags(doc, hits)
        self._fill_segments(doc, views, flag_of)
        advice = [f"{m.name}: {m.advice}" for m in sorted(metrics, key=lambda m: -m.score * m.weight)
                  if m.score >= 0.55 and m.advice]
        if score >= 50:
            advice += ["Insira especificidade humana: números reais, nomes, fontes, exemplos vividos e opinião própria.",
                       "Releia em voz alta e reescreva o que soar genérico, simétrico demais ou 'polido demais'."]
        return AnalysisResult(__version__, score, verdict_for(score), doc.word_count, warnings,
                              metrics, flags, advice, views)

    @staticmethod
    def _build_flags(doc: AnalysisDocument, hits: list[FlagHit]) -> tuple[list[Flag], dict[int, int]]:
        by_sentence: dict[int, list[FlagHit]] = {}
        for h in hits:
            by_sentence.setdefault(h.sentence, []).append(h)
        flags, flag_of = [], {}
        for n, si in enumerate(sorted(by_sentence)):
            group = by_sentence[si]
            reasons = list(dict.fromkeys(h.reason for h in group))
            suggestions = list(dict.fromkeys(h.suggestion for h in group))
            flags.append(Flag(n, doc.sentences[si].text, reasons, suggestions, len(reasons)))
            flag_of[si] = n
        return flags, flag_of

    @staticmethod
    def _fill_segments(doc: AnalysisDocument, views: list[ParagraphView], flag_of: dict[int, int]) -> None:
        by_par: dict[int, list[tuple[int, object]]] = {}
        for si, s in enumerate(doc.sentences):
            by_par.setdefault(s.paragraph, []).append((si, s))
        for pi, items in by_par.items():
            text, pos, segs = doc.paragraphs[pi].text, 0, []
            for si, s in items:
                if s.start > pos:
                    segs.append(Segment(text[pos:s.start]))
                segs.append(Segment(text[s.start:s.end], flag_of.get(si)))
                pos = s.end
            if pos < len(text):
                segs.append(Segment(text[pos:]))
            views[pi] = ParagraphView(False, segs)
