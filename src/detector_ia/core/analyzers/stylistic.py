"""Indicadores estilísticos (clichês, conectivos, pontuação, voz pessoal)."""
from __future__ import annotations

import re

from detector_ia.core.analyzers.base import Analyzer, AnalyzerOutput, FlagHit, register
from detector_ia.core.document import AnalysisDocument
from detector_ia.core.lexicon import DEFAULT_LEXICON, Lexicon
from detector_ia.core.text import ramp


@register
class TypicalPhrases(Analyzer):
    id, name, default_weight = "phrases", "Expressões e clichês típicos de I.A.", 0.22

    def _matched(self, low: str) -> dict[str, int]:
        """Expressões encontradas, descartando as contidas em outra mais longa."""
        found = {p: low.count(p) for p in self.lexicon.phrases if p in low}
        return {p: n for p, n in found.items() if not any(p != q and p in q for q in found)}

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        hits_total = self._matched(doc.lower)
        density = doc.per_1000(sum(hits_total.values()))
        top = ", ".join(f"“{p}” ×{n}" for p, n in sorted(hits_total.items(), key=lambda x: -x[1])[:5])
        hits = [
            FlagHit(i, f"Expressão típica de I.A.: “{p}”", self.lexicon.phrases[p])
            for i, s in enumerate(doc.sentences) for p in self._matched(s.text.lower())
        ]
        return AnalyzerOutput(self.metric(
            f"{density:.1f} por 1.000 palavras" + (f" — {top}" if top else ""), ramp(density, 2, 12),
            "Fórmulas como 'vale ressaltar', 'desempenha um papel crucial', 'delve' aparecem em excesso.",
            "Substitua clichês por afirmações específicas, com dados, exemplos ou nomes."), hits)


@register
class OpeningTransitions(Analyzer):
    id, name, default_weight = "transitions", "Conectivos abrindo frases", 0.12
    FLAG_THRESHOLD = 0.4

    def __init__(self, lexicon: Lexicon = DEFAULT_LEXICON) -> None:
        super().__init__(lexicon)
        self._re = re.compile(r"^(?:%s)\b" % "|".join(re.escape(t) for t in lexicon.transitions), re.I)

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        flagged = [i for i, s in enumerate(doc.sentences) if self._re.match(s.text.strip())]
        ratio = len(flagged) / max(1, len(doc.sentences))
        score = ramp(ratio, 0.08, 0.30)
        hits = []
        if score >= self.FLAG_THRESHOLD:
            hits = [FlagHit(i, "Conectivo mecânico no início da frase",
                            "Remova o conectivo ou una esta frase à anterior.") for i in flagged]
        return AnalyzerOutput(self.metric(
            f"{ratio * 100:.0f}% das frases", score,
            "Uso mecânico de 'Além disso', 'Portanto', 'Dessa forma' no início das frases.",
            "Remova conectivos desnecessários; deixe a lógica surgir da própria sequência de ideias."), hits)


@register
class PunctuationHabits(Analyzer):
    id, name, default_weight = "punctuation", "Travessões, dois-pontos e ponto e vírgula", 0.05
    FLAG_DENSITY = 6

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        low = doc.lower
        density = doc.per_1000(low.count("—") + low.count(" – ") + low.count(":") + low.count(";"))
        hits = []
        if density >= self.FLAG_DENSITY:
            hits = [FlagHit(i, "Uso de travessão (comum em texto de I.A.)",
                            "Considere trocar o travessão por vírgula ou ponto.")
                    for i, s in enumerate(doc.sentences) if "—" in s.text]
        return AnalyzerOutput(self.metric(
            f"{density:.1f} por 1.000 palavras", ramp(density, 3, 15),
            "I.A. abusa de travessões e de estruturas 'conceito: explicação'.",
            "Troque alguns travessões/dois-pontos por vírgulas ou pontos."), hits)


@register
class PersonalVoice(Analyzer):
    id, name, default_weight = "voice", "Voz pessoal e informalidade", 0.07

    def analyze(self, doc: AnalysisDocument) -> AnalyzerOutput:
        n = sum(1 for t in doc.tokens if t in self.lexicon.voice) + doc.text.count("?") + doc.text.count("!")
        density = doc.per_1000(n)
        return AnalyzerOutput(self.metric(
            f"{density:.1f} marcadores por 1.000 palavras", 1 - ramp(density, 0, 12),
            "Ausência de opinião, experiência própria ou perguntas é um sinal fraco "
            "(textos acadêmicos formais também são assim).",
            "Quando o gênero permitir, acrescente experiência, opinião ou exemplo pessoal."))
