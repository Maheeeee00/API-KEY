"""
Local Sallybus backend: curriculum + keybooks in Excel (.xlsx).

Run from repo root:
  pip install -r backend/requirements.txt
  python backend/app.py

Then open: http://127.0.0.1:5010/
(HTML is served from the parent folder; API at /api/curriculum)

Excel: data/syllabus.xlsx
  Sheet "Curriculum" — columns: Class | Subject | Unit | PageLabel | Topic
  Sheet "Keybooks"   — columns: Class | Title | File   (File = filename under /keybooks/)

Environment:
  SALLYBUS_EXCEL — path to .xlsx (default: <repo>/data/syllabus.xlsx)
  SALLYBUS_PORT  — default 5010
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from openpyxl import Workbook, load_workbook
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXCEL = ROOT / "data" / "syllabus.xlsx"
KEYBOOKS_SUBDIR = "keybooks"

EXCEL_PATH = Path(os.environ.get("SALLYBUS_EXCEL", str(DEFAULT_EXCEL))).resolve()
KEYBOOKS_DIR = (EXCEL_PATH.parent / KEYBOOKS_SUBDIR).resolve()
PORT = int(os.environ.get("SALLYBUS_PORT", "5010"))

SHEET_CURR = "Curriculum"
SHEET_KEYS = "Keybooks"
SHEET_LOG = "SyllabusLog"
HEADER_CURR = ["Class", "Subject", "Unit", "PageLabel", "Topic"]
HEADER_KEYS = ["Class", "Title", "File"]
HEADER_LOG = ["Time", "Class", "Subject", "Chapter", "Pages", "Topics", "Outline"]


def ensure_keybooks_dir() -> None:
    KEYBOOKS_DIR.mkdir(parents=True, exist_ok=True)


def curriculum_rows_to_nested(rows: list[tuple[str, str, str, str, str]]) -> dict:
    """Build curriculum dict from flat rows."""
    # class -> subject -> list of units; each unit {name, pages: [{label, topics}]}
    curriculum: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))

    # Temporary: (class, subject, unit) -> ordered list of pages with topics
    unit_pages: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    page_index: dict[tuple[str, str, str, str], dict] = {}

    for class_, subject, unit, page_label, topic in rows:
        class_ = (class_ or "").strip()
        subject = (subject or "").strip()
        unit = (unit or "").strip()
        page_label = (page_label or "").strip()
        topic = (topic or "").strip()
        if not class_ or not subject or not unit or not page_label:
            continue
        key_u = (class_, subject, unit)
        key_p = (class_, subject, unit, page_label)
        if key_p not in page_index:
            page_obj = {"label": page_label, "topics": []}
            page_index[key_p] = page_obj
            unit_pages[key_u].append(page_obj)
        if topic and topic not in page_index[key_p]["topics"]:
            page_index[key_p]["topics"].append(topic)

    # Merge units into curriculum[class][subject] as list (preserve first-seen unit order)
    seen_units: dict[tuple[str, str], list[str]] = defaultdict(list)

    for (class_, subject, unit), pages in unit_pages.items():
        if not pages:
            continue
        if unit not in seen_units[(class_, subject)]:
            seen_units[(class_, subject)].append(unit)
            curriculum[class_][subject].append({"name": unit, "pages": pages})
        else:
            # Same unit name appeared again (non-contiguous rows): merge pages
            units_list = curriculum[class_][subject]
            for uobj in units_list:
                if uobj["name"] == unit:
                    existing_labels = {p["label"] for p in uobj["pages"]}
                    for p in pages:
                        if p["label"] not in existing_labels:
                            uobj["pages"].append(p)
                            existing_labels.add(p["label"])
                        else:
                            for ep in uobj["pages"]:
                                if ep["label"] == p["label"]:
                                    for t in p["topics"]:
                                        if t not in ep["topics"]:
                                            ep["topics"].append(t)
                    break

    return {k: dict(v) for k, v in curriculum.items()}


def nested_to_curriculum_rows(curriculum: dict) -> list[tuple[str, str, str, str, str]]:
    rows: list[tuple[str, str, str, str, str]] = []
    for class_, subjects in curriculum.items():
        for subject, units in subjects.items():
            for unit in units:
                uname = unit.get("name") or ""
                for page in unit.get("pages") or []:
                    plabel = page.get("label") or ""
                    topics = page.get("topics") or []
                    if not topics:
                        rows.append((class_, subject, uname, plabel, ""))
                    else:
                        for t in topics:
                            rows.append((class_, subject, uname, plabel, str(t)))
    return rows


def read_keybooks(wb) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    if SHEET_KEYS not in wb.sheetnames:
        return {}
    ws = wb[SHEET_KEYS]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        class_, title, file_ = (str(row[0]).strip(), str(row[1] or "").strip(), str(row[2] or "").strip())
        if not class_ or not file_:
            continue
        # URL path served by this app (see /data/<path>)
        out[class_].append({"title": title or file_, "file": f"/data/{KEYBOOKS_SUBDIR}/{file_}"})
    return dict(out)


def read_bundle_from_excel() -> dict:
    if not EXCEL_PATH.is_file():
        return {"version": 1, "curriculum": {}, "keybooksByClass": {}}
    wb = load_workbook(EXCEL_PATH, read_only=True, data_only=True)
    try:
        curriculum: dict = {}
        if SHEET_CURR in wb.sheetnames:
            ws = wb[SHEET_CURR]
            rows: list[tuple[str, str, str, str, str]] = []
            for r in ws.iter_rows(min_row=2, values_only=True):
                if not r or r[0] is None:
                    continue
                rows.append(
                    (
                        str(r[0] or "").strip(),
                        str(r[1] or "").strip(),
                        str(r[2] or "").strip(),
                        str(r[3] or "").strip(),
                        str(r[4] or "").strip(),
                    )
                )
            curriculum = curriculum_rows_to_nested(rows)
        keybooks = read_keybooks(wb) if SHEET_KEYS in wb.sheetnames else {}
        return {"version": 1, "curriculum": curriculum, "keybooksByClass": keybooks}
    finally:
        wb.close()


def write_excel(curriculum: dict, keybooks_by_class: dict | None = None, preserve_log: bool = True) -> None:
    ensure_keybooks_dir()
    keybooks_by_class = keybooks_by_class or {}
    log_rows: list[list] = []
    if preserve_log and EXCEL_PATH.is_file():
        wb0 = load_workbook(EXCEL_PATH, read_only=True, data_only=True)
        try:
            if SHEET_LOG in wb0.sheetnames:
                ws0 = wb0[SHEET_LOG]
                for row in ws0.iter_rows(min_row=2, values_only=True):
                    if row and any(c is not None and str(c).strip() for c in row):
                        log_rows.append([c for c in row])
        finally:
            wb0.close()

    wb = Workbook()
    # Curriculum
    ws_c = wb.active
    ws_c.title = SHEET_CURR
    ws_c.append(HEADER_CURR)
    for row in nested_to_curriculum_rows(curriculum):
        ws_c.append(list(row))
    # Keybooks
    ws_k = wb.create_sheet(SHEET_KEYS)
    ws_k.append(HEADER_KEYS)
    for class_, items in keybooks_by_class.items():
        for item in items:
            fn = item.get("file") or ""
            fn = fn.replace("\\", "/")
            if "/" in fn:
                fn = fn.split("/")[-1]
            ws_k.append([class_, item.get("title") or fn, fn])
    # Syllabus log
    ws_l = wb.create_sheet(SHEET_LOG)
    ws_l.append(HEADER_LOG)
    for row in log_rows:
        while len(row) < len(HEADER_LOG):
            row.append("")
        ws_l.append(row[: len(HEADER_LOG)])

    EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(EXCEL_PATH)


def append_syllabus_log_row(time_str: str, class_: str, subject: str, chapter: str, pages: str, topics: str, outline: str) -> None:
    if not EXCEL_PATH.is_file():
        create_sample_excel_if_missing()
    wb = load_workbook(EXCEL_PATH)
    if SHEET_LOG not in wb.sheetnames:
        ws = wb.create_sheet(SHEET_LOG)
        ws.append(HEADER_LOG)
    else:
        ws = wb[SHEET_LOG]
        if ws.max_row == 0 or (ws.max_row == 1 and not any(ws[1][i].value for i in range(ws.max_column or 0))):
            ws.append(HEADER_LOG)
    outline_cell = (outline or "")[:32000]
    ws.append([time_str, class_, subject, chapter, pages, topics, outline_cell])
    wb.save(EXCEL_PATH)
    wb.close()


def create_sample_excel_if_missing() -> None:
    if EXCEL_PATH.is_file():
        return
    sample = (ROOT / "data" / "syllabus-by-class.json").read_text(encoding="utf-8")
    data = json.loads(sample)
    write_excel(data)


app = Flask(__name__, static_folder=None)
CORS(app)


@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "excel": str(EXCEL_PATH), "exists": EXCEL_PATH.is_file()})


@app.route("/api/curriculum", methods=["GET", "POST", "OPTIONS"])
def api_curriculum():
    if request.method == "OPTIONS":
        return "", 204
    if request.method == "GET":
        create_sample_excel_if_missing()
        bundle = read_bundle_from_excel()
        return jsonify(bundle)
    body = request.get_json(force=True, silent=True) or {}
    curriculum = body.get("curriculum")
    if not isinstance(curriculum, dict):
        return jsonify({"error": "Missing curriculum object"}), 400
    keybooks = body.get("keybooksByClass")
    if keybooks is not None and not isinstance(keybooks, dict):
        return jsonify({"error": "keybooksByClass must be an object"}), 400
    existing = read_bundle_from_excel()
    merged_keys: dict = dict(existing.get("keybooksByClass") or {})
    if isinstance(keybooks, dict):
        for k, v in keybooks.items():
            merged_keys[k] = v
    write_excel(curriculum, merged_keys, preserve_log=True)
    return jsonify({"ok": True, "saved": str(EXCEL_PATH)})


@app.route("/api/keybook", methods=["POST", "OPTIONS"])
def api_keybook():
    if request.method == "OPTIONS":
        return "", 204
    ensure_keybooks_dir()
    class_ = (request.form.get("class") or "").strip()
    title = (request.form.get("title") or "").strip()
    if "file" not in request.files or not class_:
        return jsonify({"error": "Need class and file"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400
    raw = secure_filename(f.filename)
    if not raw.lower().endswith(".pdf"):
        raw = raw + ".pdf" if "." not in raw else raw
    dest = KEYBOOKS_DIR / raw
    f.save(dest)
    rel = f"/data/{KEYBOOKS_SUBDIR}/{dest.name}"
    bundle = read_bundle_from_excel()
    kb = bundle.get("keybooksByClass") or {}
    lst = kb.get(class_) or []
    lst.append({"title": title or dest.name, "file": rel})
    kb[class_] = lst
    write_excel(bundle.get("curriculum") or {}, kb, preserve_log=True)
    return jsonify({"ok": True, "file": rel})


@app.route("/api/syllabus-log", methods=["POST", "OPTIONS"])
def api_syllabus_log():
    if request.method == "OPTIONS":
        return "", 204
    body = request.get_json(force=True, silent=True) or {}

    append_syllabus_log_row(
        datetime.now().isoformat(timespec="seconds"),
        str(body.get("class") or ""),
        str(body.get("subject") or ""),
        str(body.get("chapter") or ""),
        str(body.get("pages") or ""),
        str(body.get("topics") or ""),
        str(body.get("outline") or ""),
    )
    return jsonify({"ok": True})


@app.route("/keybooks/<path:name>")
def serve_keybook(name):
    ensure_keybooks_dir()
    return send_from_directory(KEYBOOKS_DIR, name, as_attachment=False)


@app.route("/data/<path:fname>")
def serve_data(fname):
    return send_from_directory(ROOT / "data", fname)


@app.route("/")
def index():
    return send_from_directory(ROOT, "sallybus generator.html")


@app.route("/<path:filename>")
def static_files(filename):
    if ".." in filename or filename.startswith("/"):
        return "Not found", 404
    target = ROOT / filename
    if target.is_file():
        return send_from_directory(ROOT, filename)
    return "Not found", 404


if __name__ == "__main__":
    create_sample_excel_if_missing()
    print("Sallybus backend")
    print("  Excel:", EXCEL_PATH)
    print("  Keybooks:", KEYBOOKS_DIR)
    print("  Open: http://127.0.0.1:%s/" % PORT)
    app.run(host="127.0.0.1", port=PORT, debug=True)
