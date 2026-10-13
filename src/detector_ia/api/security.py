"""Autenticação por chave de API e limitação de taxa."""
from __future__ import annotations

import hashlib
import hmac
import threading
import time
from collections import deque

from fastapi import Header, HTTPException, Request

from detector_ia.config import Settings


class SlidingWindowRateLimiter:
    """Limitador em memória (por processo). Para várias instâncias, troque por Redis
    mantendo a mesma interface `allow(key)`."""

    def __init__(self, limit: int, window: float = 60.0) -> None:
        self.limit, self.window = limit, window
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        if self.limit <= 0:
            return True
        now = time.monotonic()
        with self._lock:
            if len(self._hits) > 10_000:  # evita crescimento ilimitado
                self._hits = {k: v for k, v in self._hits.items() if v and now - v[-1] < self.window}
            q = self._hits.setdefault(key, deque())
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True


def _valid_key(candidate: str | None, keys: tuple[str, ...]) -> bool:
    if not candidate:
        return False
    ok = False
    for k in keys:  # percorre todas para tempo constante
        ok |= hmac.compare_digest(candidate.encode(), k.encode())
    return ok


def build_guard(settings: Settings, limiter: SlidingWindowRateLimiter):
    """Dependência FastAPI: valida a chave (se configurada) e aplica rate limit."""

    async def guard(request: Request, x_api_key: str | None = Header(default=None)) -> str:
        if settings.api_keys and not _valid_key(x_api_key, settings.api_keys):
            raise HTTPException(401, "Chave de API ausente ou inválida.")
        ident = hashlib.sha256((x_api_key or "").encode()).hexdigest()[:16] if x_api_key else (
            request.client.host if request.client else "unknown")
        if not limiter.allow(ident):
            raise HTTPException(429, "Muitas requisições. Tente novamente em instantes.",
                                headers={"Retry-After": "60"})
        return ident

    return guard
