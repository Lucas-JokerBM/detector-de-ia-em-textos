"""App desktop: janela nativa (pywebview) exibindo a MESMA interface web.

Modos:
  local  -> sobe o servidor embutido em 127.0.0.1 (porta aleatória, chave de sessão).
  remote -> abre o servidor hospedado; nenhum código do motor vai no executável
            (melhor proteção contra cópia).
"""
from __future__ import annotations

import argparse
import os
import secrets
import threading
import time
from urllib.parse import quote, urlparse

TITLE = "Detector de I.A. em documentos .docx"


def _start_local_server() -> tuple[object, str]:
    import uvicorn  # importação tardia: o modo remote não precisa disso

    from detector_ia.api.app import create_app
    from detector_ia.config import Settings

    token = secrets.token_urlsafe(32)  # impede que outros processos/sites usem o servidor local
    app = create_app(Settings(api_keys=(token,), rate_limit_per_minute=0))
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.1)
    else:
        raise RuntimeError("O servidor local não iniciou.")
    port = server.servers[0].sockets[0].getsockname()[1]
    return server, f"http://127.0.0.1:{port}/#key={quote(token)}"


def _validate_remote(url: str) -> str:
    p = urlparse(url)
    if p.scheme != "https" and p.hostname not in {"localhost", "127.0.0.1"}:
        raise SystemExit("A URL remota deve usar HTTPS.")
    return url


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["local", "remote"], default=os.environ.get("DETECTOR_MODE", "local"))
    ap.add_argument("--url", default=os.environ.get("DETECTOR_REMOTE_URL", ""))
    args = ap.parse_args()

    import webview  # pywebview

    server = None
    if args.mode == "remote":
        if not args.url:
            raise SystemExit("Informe --url ou DETECTOR_REMOTE_URL no modo remote.")
        url = _validate_remote(args.url)
    else:
        server, url = _start_local_server()
    try:
        webview.create_window(TITLE, url, width=1280, height=820, min_size=(900, 600))
        webview.start()
    finally:
        if server is not None:
            server.should_exit = True


if __name__ == "__main__":
    main()
