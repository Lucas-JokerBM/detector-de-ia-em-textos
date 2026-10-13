"""Gera o executável desktop com Nuitka (compila Python -> C -> binário nativo).

  python scripts/build_desktop.py --mode remote   # recomendado: sem o motor no executável
  python scripts/build_desktop.py --mode local    # offline: inclui o motor (compilado)

Requer: pip install -e ".[desktop,api,build]" e um compilador C (MSVC no Windows, gcc/clang no Linux/macOS).
Rode no sistema operacional de destino (não há cross-compile).
"""
from __future__ import annotations

import argparse
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--mode", choices=["local", "remote"], default="remote")
args = ap.parse_args()

cmd = [
    sys.executable, "-m", "nuitka", "--onefile", "--output-dir=dist", "--output-filename=detector-ia",
    "--assume-yes-for-downloads", "--remove-output",
]
if sys.platform == "win32":
    cmd.append("--windows-console-mode=disable")  # em versões antigas do Nuitka: --windows-disable-console
if args.mode == "remote":
    # O executável é só um "navegador" dedicado: o motor, a API e o léxico NÃO são empacotados.
    cmd += ["--nofollow-import-to=detector_ia.core,detector_ia.api,detector_ia.service,fastapi,uvicorn,defusedxml"]
else:
    cmd += ["--include-package=detector_ia", "--include-package-data=detector_ia"]
cmd.append("src/detector_ia/desktop/launcher.py")

print(" ".join(cmd))
raise SystemExit(subprocess.call(cmd))
