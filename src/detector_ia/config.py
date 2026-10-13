"""Configuração centralizada (12-factor): tudo vem de variáveis de ambiente."""
from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from detector_ia.core.docx_reader import DocxLimits


def _csv(value: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in value.split(",") if x.strip())


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8000
    max_upload_bytes: int = 5 * 1024 * 1024
    max_uncompressed_bytes: int = 50 * 1024 * 1024
    max_compression_ratio: int = 200
    api_keys: tuple[str, ...] = ()
    rate_limit_per_minute: int = 30
    cors_origins: tuple[str, ...] = ()
    enable_docs: bool = False
    log_level: str = "INFO"
    weights: Mapping[str, float] = field(default_factory=dict)

    @property
    def docx_limits(self) -> DocxLimits:
        return DocxLimits(
            max_bytes=self.max_upload_bytes,
            max_uncompressed_bytes=self.max_uncompressed_bytes,
            max_ratio=self.max_compression_ratio,
        )

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        e = os.environ if env is None else env
        g = lambda k, d="": e.get(f"DETECTOR_{k}", d)  # noqa: E731
        return cls(
            host=g("HOST", "127.0.0.1"),
            port=int(g("PORT", "8000")),
            max_upload_bytes=int(float(g("MAX_UPLOAD_MB", "5")) * 1024 * 1024),
            api_keys=_csv(g("API_KEYS")),
            rate_limit_per_minute=int(g("RATE_LIMIT_PER_MINUTE", "30")),
            cors_origins=_csv(g("CORS_ORIGINS")),
            enable_docs=_bool(g("ENABLE_DOCS", "false")),
            log_level=g("LOG_LEVEL", "INFO").upper(),
            weights=json.loads(g("WEIGHTS", "{}") or "{}"),
        )
