import base64
import io
import logging
import re
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader

logger = logging.getLogger(__name__)

app = FastAPI(
    title="PDF to Text API",
    description="Upload a PDF file and receive extracted plain text.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MiB


class PdfToTextJsonBody(BaseModel):
    """Body for Google Apps Script / clients that send base64 (no multipart)."""

    pdf_base64: str = Field(..., min_length=1, description="Raw base64 or data URL")
    file_name: str = Field(default="upload.pdf", max_length=512)


def _normalize_pdf_filename(name: str) -> str:
    n = (name or "").strip() or "upload.pdf"
    if not n.lower().endswith(".pdf"):
        n += ".pdf"
    return n


def _decode_pdf_base64(b64: str) -> bytes:
    s = (b64 or "").strip()
    if s.startswith("data:") and "base64," in s:
        s = s.split("base64,", 1)[1]
    s = re.sub(r"\s+", "", s)
    try:
        raw = base64.b64decode(s, validate=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding.") from e
    if not raw:
        raise HTTPException(status_code=400, detail="Decoded PDF is empty.")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MiB.",
        )
    if not raw.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="Decoded bytes do not look like a PDF (missing %PDF header).",
        )
    return raw


def _extract_text_from_pdf_bytes(raw: bytes, filename: str) -> dict[str, str | int]:
    try:
        reader = PdfReader(io.BytesIO(raw))
    except Exception as e:
        logger.exception("Invalid PDF")
        raise HTTPException(
            status_code=400,
            detail="Could not read PDF. The file may be corrupted or not a valid PDF.",
        ) from e

    parts: list[str] = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as e:
            logger.warning("Failed to extract page %s: %s", i + 1, e)
            text = ""
        parts.append(text)

    full_text = "\n\n".join(parts).strip()
    return {
        "filename": filename,
        "pages": len(reader.pages),
        "text": full_text,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/pdf-to-text-json")
def pdf_to_text_json(body: PdfToTextJsonBody) -> dict[str, str | int]:
    """
    Same as /pdf-to-text but accepts JSON `{ "pdf_base64": "...", "file_name": "x.pdf" }`.
    Use this from Google Apps Script with UrlFetchApp (multipart is awkward there).
    """
    fname = _normalize_pdf_filename(body.file_name)
    raw = _decode_pdf_base64(body.pdf_base64)
    return _extract_text_from_pdf_bytes(raw, fname)


@app.post("/pdf-to-text")
async def pdf_to_text(
    file: Annotated[UploadFile, File(description="PDF document")],
) -> dict[str, str | int]:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Expected a file with .pdf extension.",
        )

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file.")

    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MiB.",
        )

    return _extract_text_from_pdf_bytes(raw, file.filename)
