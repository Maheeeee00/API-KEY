#!/usr/bin/env python3
"""
Build ONE file the HTML can load: data/sallybus-bundle.json

  - curriculum: class → subject → chapters (same shape as syllabus-by-class.json)
  - keybooksByClass: class name → list of { "title", "file" } where file is a path
    relative to the HTML page (default: data/keybooks/<filename>)

Sources:
  1) Copy or download PDFs listed in a config file.
  2) Wrap existing data/syllabus-by-class.json as curriculum (or set in config).

Config (JSON) example — save as tools/build-bundle-config.json:

{
  "outputBundle": "data/sallybus-bundle.json",
  "keybooksDir": "data/keybooks",
  "curriculumFile": "data/syllabus-by-class.json",
  "downloads": [
    {
      "class": "Class 2",
      "title": "Skillup English keybook 2",
      "source": "C:\\\\Users\\\\laptop World\\\\Downloads\\\\Skillup English keybook 2.pdf"
    },
    {
      "class": "Class 3",
      "title": "Skillup English keybook 3",
      "source": "https://example.com/book3.pdf"
    }
  ]
}

Run from repo root:
  python tools/build_sallybus_bundle.py tools/build-bundle-config.json

If no config path is passed, looks for tools/build-bundle-config.json
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path


def slug_filename(class_name: str, title: str, index: int) -> str:
    safe = re.sub(r"[^\w\-]+", "-", f"{class_name}-{title}", flags=re.UNICODE)
    safe = re.sub(r"-+", "-", safe).strip("-") or f"class-{index}"
    return safe[:120] + ".pdf"


def fetch_or_copy(source: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.startswith("http://") or source.startswith("https://"):
        print(f"  Download: {source[:80]}...")
        urllib.request.urlretrieve(source, dest)
    else:
        src = Path(source)
        if not src.is_file():
            raise FileNotFoundError(f"Not a file: {source}")
        print(f"  Copy: {src.name}")
        shutil.copy2(src, dest)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build sallybus-bundle.json for the HTML app.")
    parser.add_argument(
        "config",
        nargs="?",
        type=Path,
        default=root / "tools" / "build-bundle-config.json",
        help="JSON config path (default: tools/build-bundle-config.json)",
    )
    args = parser.parse_args()
    cfg_path: Path = args.config
    if not cfg_path.is_file():
        print(
            "Missing config. Create tools/build-bundle-config.json — see docstring in this script.",
            file=sys.stderr,
        )
        sys.exit(1)

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    out_rel = cfg.get("outputBundle", "data/sallybus-bundle.json")
    kb_dir_rel = cfg.get("keybooksDir", "data/keybooks")
    cur_rel = cfg.get("curriculumFile", "data/syllabus-by-class.json")

    out_path = root / out_rel
    kb_dir = root / kb_dir_rel
    cur_path = root / cur_rel

    if not cur_path.is_file():
        print(f"Missing curriculum file: {cur_path}", file=sys.stderr)
        sys.exit(1)

    curriculum = json.loads(cur_path.read_text(encoding="utf-8"))
    keybooks_by_class: dict[str, list[dict[str, str]]] = {}

    downloads = cfg.get("downloads") or []
    for i, item in enumerate(downloads):
        cls = (item.get("class") or "").strip()
        title = (item.get("title") or "Keybook").strip()
        source = (item.get("source") or "").strip()
        if not cls or not source:
            print(f"Skip invalid entry #{i}: need class and source", file=sys.stderr)
            continue
        fname = item.get("filename") or slug_filename(cls, title, i)
        if not fname.lower().endswith(".pdf"):
            fname += ".pdf"
        dest_abs = kb_dir / fname
        rel_for_html = str(Path(kb_dir_rel) / fname).replace("\\", "/")
        print(f"{cls} / {title} -> {rel_for_html}")
        fetch_or_copy(source, dest_abs)
        keybooks_by_class.setdefault(cls, []).append({"title": title, "file": rel_for_html})

    bundle = {"version": 1, "curriculum": curriculum, "keybooksByClass": keybooks_by_class}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote: {out_path}")
    print("Point sallybus generator.html at this file (SYLLABUS_DATA_URL) or keep default data/sallybus-bundle.json")


if __name__ == "__main__":
    main()
