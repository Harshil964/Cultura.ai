"""Turns an uploaded screenplay file (PDF/DOCX/TXT) into plain text.

Kept deliberately dumb: no scene splitting or entity logic here — that's
the extraction_agent's job. This module only answers "what does the file
say", nothing more.
"""
from __future__ import annotations

import io

import fitz  # PyMuPDF
import docx  # python-docx


class UnsupportedFileType(ValueError):
    pass


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    if ext == "docx":
        return _extract_docx(file_bytes)
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="replace")

    raise UnsupportedFileType(f"Unsupported file type: .{ext}. Use PDF, DOCX, or TXT.")


def _extract_pdf(file_bytes: bytes) -> str:
    text_parts: list[str] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()


def _extract_docx(file_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in document.paragraphs).strip()
