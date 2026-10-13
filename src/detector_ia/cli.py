"""Interface de linha de comando."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from detector_ia.core.docx_reader import DocxError
from detector_ia.core.report import build_text_report
from detector_ia.service import AnalysisService


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="detector-ia", description=__doc__)
    ap.add_argument("arquivo", type=Path, help="documento .docx")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    args = ap.parse_args(argv)
    try:
        result = AnalysisService().analyze_bytes(args.arquivo.read_bytes())
    except (DocxError, OSError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2) if args.json
          else build_text_report(result, args.arquivo.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
