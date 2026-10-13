"""Indicadores estatísticos (ritmo, uniformidade, repetição, diversidade)."""
from __future__ import annotations

import statistics
from collections import Counter

from detector_ia.core.analyzers.base import Analyzer, AnalyzerOutput, FlagHit, register
from detector_ia.core.document import AnalysisDocument
from detector_ia.core.text import coeff_variation, mattr, ramp


@register
class SentenceVariation(Analyzer):
    id, name, default_weight = "sentence_variation", "Variação do tamanho das frases", 0.22

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        lens = [len(s.tokens) for s in doc.sentences]
        expl = "Humanos alternam frases curtas e longas; I.A. tende a produzir frases de tamanho parecido."
        if len(lens) < 8:
            return AnalyzerOutput(self.metric("poucas frases", 0.5, expl))
        c = coeff_variation(lens)
        return AnalyzerOutput(self.metric(
            f"CV = {c:.2f} (média {statistics.mean(lens):.1f} palavras)", 1 - ramp(c, 0.35, 0.70), expl,
            "Alterne frases curtas (5–10 palavras) com frases mais longas e complexas."))


@register
class ParagraphUniformity(Analyzer):
    id, name, default_weight = "paragraph_uniformity", "Uniformidade dos parágrafos", 0.08

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        expl = "Parágrafos quase do mesmo tamanho sugerem geração padronizada."
        if len(doc.paragraph_lengths) < 5:
            return AnalyzerOutput(self.metric("poucos parágrafos", 0.5, expl))
        c = coeff_variation(doc.paragraph_lengths)
        return AnalyzerOutput(self.metric(
            f"CV = {c:.2f}", 1 - ramp(c, 0.25, 0.65), expl,
            "Deixe alguns parágrafos curtos e outros mais desenvolvidos, conforme a ideia."))


@register
class TrigramRepetition(Analyzer):
    id, name, default_weight = "trigram_repetition", "Repetição de trechos (trigramas)", 0.08

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        t = doc.tokens
        tri = Counter(zip(t, t[1:], t[2:], strict=False))
        rep = sum(v for v in tri.values() if v > 1) / max(1, sum(tri.values()))
        return AnalyzerOutput(self.metric(
            f"{rep * 100:.1f}%", ramp(rep, 0.01, 0.06),
            "Reaproveitamento frequente das mesmas sequências de palavras.",
            "Reformule trechos repetidos ou elimine redundâncias."))


@register
class LexicalDiversity(Analyzer):
    id, name, default_weight = "lexical_diversity", "Diversidade de vocabulário (MATTR)", 0.06

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        expl = "Vocabulário mais restrito e previsível pode indicar geração automática."
        m = mattr(doc.tokens)
        if m is None:
            return AnalyzerOutput(self.metric("texto curto", 0.5, expl))
        return AnalyzerOutput(self.metric(
            f"{m:.2f}", 1 - ramp(m, 0.62, 0.78), expl, "Use sinônimos naturais e termos próprios do seu domínio."))


@register
class RepeatedOpeners(Analyzer):
    id, name, default_weight = "openers", "Repetição de aberturas de frase", 0.10

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        key = lambda toks: " ".join(toks[:2])  # noqa: E731
        counts = Counter(key(s.tokens) for s in doc.sentences if len(s.tokens) >= 3)
        repeated = {k for k, v in counts.items() if v >= 3 and k}
        total = max(1, len(doc.sentences))
        ratio = sum(counts[k] for k in repeated) / total
        hits = [
            FlagHit(i, f"Abertura repetida ({counts[key(s.tokens)]}× no texto): “{key(s.tokens)} …”",
                    "Reescreva o início da frase para variar o ritmo.")
            for i, s in enumerate(doc.sentences) if key(s.tokens) in repeated
        ]
        return AnalyzerOutput(self.metric(
            f"{ratio * 100:.0f}% das frases", ramp(ratio, 0.08, 0.30),
            "Frases que começam sempre do mesmo jeito indicam padrão mecânico.",
            "Varie o início das frases (sujeito, circunstância, pergunta, dado)."), hits)


@register
class LongSentences(Analyzer):
    """Sem peso no score: apenas gera sugestões de legibilidade."""

    id, name, default_weight = "long_sentences", "Frases muito longas", 0.0
    LIMIT = 40

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        hits = [FlagHit(i, f"Frase muito longa ({len(s.tokens)} palavras)",
                        "Divida em duas ou três frases mais curtas.")
                for i, s in enumerate(doc.sentences) if len(s.tokens) > self.LIMIT]
        return AnalyzerOutput(None, hits)
