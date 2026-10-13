"""Importar os módulos registra os analisadores padrão (veja base.register)."""
from detector_ia.core.analyzers import statistical, stylistic  # noqa: F401
from detector_ia.core.analyzers.base import Analyzer, AnalyzerOutput, FlagHit, default_analyzers, register

__all__ = ["Analyzer", "AnalyzerOutput", "FlagHit", "default_analyzers", "register"]
