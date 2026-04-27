#!/usr/bin/env python3
"""
Merge Skillup English keybooks + Final Book 7 + any PDFs inside the ZIP into one PDF.

Run on YOUR Windows machine (where the files exist). Requires:
    pip install pypdf

Usage:
    python tools/merge_skillup_pdfs.py
    python tools/merge_skillup_pdfs.py -o "C:\\Users\\laptop World\\Downloads\\sallybus\\merged.pdf"
"""

from __future__ import annotations

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path

# Merged PDF is written here by default (create the folder if it does not exist).
DEFAULT_OUTPUT_DIR = Path(r"C:\Users\laptop World\Downloads\sallybus")

# --- Edit these paths if your files moved (same order you listed) ---
DEFAULT_FILES = [
    r"C:\Users\laptop World\Downloads\Skillup English keybook 4.pdf",
    r"C:\Users\laptop World\Downloads\Skillup English keybook 3.pdf",
    r"C:\Users\laptop World\Downloads\Skillup English keybook 5.pdf",
    r"C:\Users\laptop World\Downloads\Skillup English keybook 2.pdf",
    r"C:\Users\laptop World\Downloads\Final Book 7.pdf",
    r"C:\Users\laptop World\Downloads\Keybook-20260427T055214Z-3-001.zip",
]


def import_pdf_lib():
    try:
        from pypdf import PdfReader, PdfWriter

        return PdfReader, PdfWriter
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfReader, PdfWriter

        return PdfReader, PdfWriter
    except ImportError:
        print(
            "Install pypdf first:\n  pip install pypdf",
            file=sys.stderr,
        )
        sys.exit(1)


def pdf_paths_from_zip(zip_path: Path, tmpdir: Path) -> list[Path]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(tmpdir)
    pdfs = sorted(tmpdir.rglob("*.pdf"), key=lambda p: str(p).lower())
    if not pdfs:
        print(f"Warning: no PDF files found inside {zip_path}", file=sys.stderr)
    return pdfs


def append_pdf(writer, reader_cls, path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Missing file: {path}")
    reader = reader_cls(str(path))
    for page in reader.pages:
        writer.add_page(page)


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge keybook PDFs (+ PDFs in ZIP) into one file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "Skillup_keybooks_merged.pdf",
        help="Output merged PDF path (default: Downloads\\sallybus\\Skillup_keybooks_merged.pdf)",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="Optional: override input files (PDF or ZIP). Default uses script DEFAULT_FILES.",
    )
    args = parser.parse_args()

    PdfReader, PdfWriter = import_pdf_lib()
    writer = PdfWriter()
    files = [Path(p) for p in args.inputs] if args.inputs else [Path(p) for p in DEFAULT_FILES]

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for f in files:
            suf = f.suffix.lower()
            if suf == ".pdf":
                print(f"Adding: {f.name}")
                append_pdf(writer, PdfReader, f)
            elif suf == ".zip":
                print(f"Extracting ZIP: {f.name}")
                sub = tmpdir / f.stem
                sub.mkdir(parents=True, exist_ok=True)
                for pdf in pdf_paths_from_zip(f, sub):
                    try:
                        rel = pdf.relative_to(sub)
                    except ValueError:
                        rel = pdf.name
                    print(f"  Adding from ZIP: {rel}")
                    append_pdf(writer, PdfReader, pdf)
            else:
                print(f"Skipping (not PDF/ZIP): {f}", file=sys.stderr)

    out: Path = args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as fp:
        writer.write(fp)
    print(f"\nDone. Merged PDF saved to:\n  {out.resolve()}")


if __name__ == "__main__":
    main()
