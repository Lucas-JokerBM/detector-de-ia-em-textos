"""Leitura segura de .docx.

Defesas: limite de tamanho, validação de assinatura ZIP, proteção contra zip-bomb
(tamanho descompactado e razão de compressão) e XML parser endurecido (defusedxml)
contra XXE e "billion laughs".
"""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

from defusedxml import ElementTree as SafeET
from defusedxml.common import DefusedXmlException

from detector_ia.core.models import Paragraph

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_HEADING_RE = re.compile(r"^(heading|title|subtitle|t[ií]tulo|ttulo|subt[ií]tulo|subttulo)", re.I)
_MAIN_PART = "word/document.xml"


class DocxError(ValueError):
    """Arquivo inválido, corrompido ou que viola os limites de segurança."""


class DocxTooLargeError(DocxError):
    """Arquivo excede o tamanho máximo permitido."""


@dataclass(frozen=True)
class DocxLimits:
    max_bytes: int = 5 * 1024 * 1024
    max_uncompressed_bytes: int = 50 * 1024 * 1024
    max_ratio: int = 200


def read_docx(source: bytes | str | Path, limits: DocxLimits | None = None) -> list[Paragraph]:
    limits = limits or DocxLimits()
    data = source if isinstance(source, bytes) else Path(source).read_bytes()
    if len(data) > limits.max_bytes:
        raise DocxTooLargeError(f"Arquivo maior que o limite de {limits.max_bytes // (1024 * 1024)} MB.")
    if not data.startswith(b"PK"):
        raise DocxError("O arquivo não é um .docx válido.")

    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            try:
                info = z.getinfo(_MAIN_PART)
            except KeyError as exc:
                raise DocxError("Estrutura .docx inválida (document.xml ausente).") from exc
            if info.file_size > limits.max_uncompressed_bytes:
                raise DocxError("Conteúdo descompactado excede o limite permitido.")
            if info.file_size / max(1, info.compress_size) > limits.max_ratio:
                raise DocxError("Razão de compressão suspeita (possível zip-bomb).")
            with z.open(info) as fh:
                xml = fh.read(limits.max_uncompressed_bytes + 1)
            if len(xml) > limits.max_uncompressed_bytes:
                raise DocxError("Conteúdo descompactado excede o limite permitido.")
    except zipfile.BadZipFile as exc:
        raise DocxError("Arquivo corrompido ou protegido por senha.") from exc

    try:
        root = SafeET.fromstring(xml, forbid_dtd=True)
    except (SafeET.ParseError, DefusedXmlException) as exc:
        raise DocxError("XML do documento inválido ou potencialmente malicioso.") from exc

    paragraphs: list[Paragraph] = []
    for p in root.iter(_W + "p"):
        style = ""
        ppr = p.find(_W + "pPr")
        if ppr is not None:
            ps = ppr.find(_W + "pStyle")
            if ps is not None:
                style = ps.get(_W + "val", "")
        parts: list[str] = []
        for el in p.iter():
            if el.tag == _W + "t":
                parts.append(el.text or "")
            elif el.tag in (_W + "tab", _W + "br", _W + "cr"):
                parts.append(" ")
        text = re.sub(r"\s+", " ", "".join(parts)).strip()
        if text:
            paragraphs.append(Paragraph(text=text, style=style, is_heading=bool(_HEADING_RE.match(style))))
    return paragraphs
