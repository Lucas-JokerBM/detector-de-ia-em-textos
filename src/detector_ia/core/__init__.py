"""Núcleo de domínio: sem dependência de web, desktop ou frameworks."""
from detector_ia.core.engine import AnalysisEngine
from detector_ia.core.models import AnalysisResult, Paragraph

__all__ = ["AnalysisEngine", "AnalysisResult", "Paragraph"]
