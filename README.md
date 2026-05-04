# startwell — syllabus generator

Single-page app (`index.html`) plus Google Apps Script (`Code.gs`).

## Flow

1. **PDF → text** in the browser (PDF.js).
2. **Structure** with Cursor (paste prompt → paste **JSON** or **TSV/CSV table**) or an optional OpenAI-compatible API key on a **private** copy only.
3. **Save** to Google Sheet via deployed Web App (`saveStructured`).

## Setup

1. Copy `Code.gs` into Apps Script, set `SHEET_ID`, run `setupSheet`, deploy **Web App** (Execute as: Me, Anyone with the link).
2. In `index.html`, set `SCRIPT_URL` to your deployment URL.
3. Do **not** commit real API keys in public HTML.
