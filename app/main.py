import io
import logging
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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
        "filename": file.filename,
        "pages": len(reader.pages),
        "text": full_text,
    }
