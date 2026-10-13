"""Camada de aplicação: casos de uso reutilizados por CLI, API e desktop (modo local)."""
from __future__ import annotations

import logging
import time

from detector_ia.config import Settings
from detector_ia.core.docx_reader import read_docx
from detector_ia.core.engine import AnalysisEngine
from detector_ia.core.models import AnalysisResult

log = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self, settings: Settings | None = None, engine: AnalysisEngine | None = None) -> None:
        self.settings = settings or Settings()
        self.engine = engine or AnalysisEngine(weights=self.settings.weights)

    def analyze_bytes(self, data: bytes) -> AnalysisResult:
        t0 = time.perf_counter()
        result = self.engine.analyze(read_docx(data, self.settings.docx_limits))
        # Nunca registre o conteúdo do documento (privacidade).
        log.info("analysis ok words=%d score=%.0f ms=%d", result.words, result.score,
                 (time.perf_counter() - t0) * 1000)
        return result
