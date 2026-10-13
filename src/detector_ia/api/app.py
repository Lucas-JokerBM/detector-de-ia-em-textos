"""Aplicação web (FastAPI): API REST versionada + interface web estática.

A análise roda SEMPRE no servidor: o cliente (navegador ou app desktop remoto)
nunca recebe o código-fonte do motor.
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles

from detector_ia import __version__
from detector_ia.api.schemas import AnalysisOut, HealthOut
from detector_ia.api.security import SlidingWindowRateLimiter, build_guard
from detector_ia.config import Settings
from detector_ia.core.docx_reader import DocxError, DocxTooLargeError
from detector_ia.service import AnalysisService

STATIC_DIR = Path(__file__).resolve().parent.parent / "web" / "static"
CSP = ("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
       "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
_CHUNK = 64 * 1024


async def _read_limited(file: UploadFile, limit: int) -> bytes:
    size, chunks = 0, []
    while chunk := await file.read(_CHUNK):
        size += len(chunk)
        if size > limit:
            raise HTTPException(413, f"Arquivo maior que {limit // (1024 * 1024)} MB.")
        chunks.append(chunk)
    return b"".join(chunks)


def create_app(settings: Settings | None = None, service: AnalysisService | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    service = service or AnalysisService(settings)
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    app = FastAPI(
        title="Detector de I.A. em .docx", version=__version__,
        docs_url="/api/docs" if settings.enable_docs else None,
        redoc_url=None, openapi_url="/api/openapi.json" if settings.enable_docs else None,
    )
    if settings.cors_origins:
        app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins),
                           allow_methods=["GET", "POST"], allow_headers=["X-API-Key"])

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.update({
            "Content-Security-Policy": CSP, "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
        })
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    guard = build_guard(settings, SlidingWindowRateLimiter(settings.rate_limit_per_minute))
    router = APIRouter(prefix="/api/v1")

    @router.get("/health", response_model=HealthOut)
    async def health() -> dict:
        return {"status": "ok", "version": __version__}

    @router.post("/analyze", response_model=AnalysisOut, dependencies=[Depends(guard)])
    async def analyze(request: Request, file: UploadFile = File(...)) -> dict:
        if not (file.filename or "").lower().endswith(".docx"):
            raise HTTPException(415, "Envie um arquivo .docx.")
        declared = request.headers.get("content-length")
        if declared and declared.isdigit() and int(declared) > settings.max_upload_bytes + 8192:
            raise HTTPException(413, "Arquivo excede o tamanho máximo permitido.")
        data = await _read_limited(file, settings.max_upload_bytes)
        try:  # CPU-bound: fora do event loop
            result = await run_in_threadpool(service.analyze_bytes, data)
        except DocxTooLargeError as exc:
            raise HTTPException(413, str(exc)) from exc
        except DocxError as exc:
            raise HTTPException(422, str(exc)) from exc
        return result.to_dict()

    app.include_router(router)
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="web")
    return app
