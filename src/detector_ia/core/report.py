"""Relatório textual (CLI/exportação)."""
from __future__ import annotations

from detector_ia.core.models import AnalysisResult


def build_text_report(result: AnalysisResult, filename: str = "") -> str:
    lines = ["RELATÓRIO — Detector de texto gerado por I.A.", f"Arquivo: {filename or '-'}", "=" * 70,
             f"Pontuação de probabilidade de I.A.: {result.score:.0f}/100", f"Parecer: {result.verdict}",
             f"Palavras analisadas: {result.words}", ""]
    lines += [f"[!] {w}" for w in result.warnings]
    lines += ["", "INDICADORES", "-" * 70]
    for m in result.metrics:
        lines += [f"* {m.name}: {m.value}  -> sinal {m.score * 100:.0f}%", f"    {m.explanation}"]
    lines += ["", "SUGESTÕES GERAIS", "-" * 70]
    lines += [f"- {a}" for a in result.global_advice] or ["- Nenhuma sugestão geral relevante."]
    lines += ["", f"TRECHOS SINALIZADOS ({len(result.flags)})", "-" * 70]
    for f in result.flags:
        lines.append(f"{f.id + 1}. “{f.text}”")
        lines += [f"     Motivo: {r}" for r in f.reasons] + [f"     Sugestão: {s}" for s in f.suggestions]
    lines += ["", "Aviso: análise heurística; não constitui prova de autoria."]
    return "\n".join(lines)
