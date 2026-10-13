"""Entrada de produção: `detector-ia-server`."""
from __future__ import annotations

import os

import uvicorn

from detector_ia.config import Settings


def main() -> None:
    s = Settings.from_env()
    uvicorn.run("detector_ia.api.app:create_app", factory=True, host=s.host, port=s.port,
                workers=int(os.environ.get("DETECTOR_WORKERS", "1")), log_level=s.log_level.lower(),
                proxy_headers=True, server_header=False)


if __name__ == "__main__":
    main()
