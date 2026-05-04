# startwell — syllabus generator

Single-page app (`index.html`) plus Google Apps Script (`Code.gs`).

## Flow

1. **PDF → text** in the browser (PDF.js).
2. **Structure** with Cursor (paste prompt → paste **JSON** or **TSV/CSV table**) or an optional OpenAI-compatible API key on a **private** copy only.
3. **Save** to Google Sheet via deployed Web App (`saveStructured`).

## Sheet columns (SyllabusData)

After the first `setupSheet`, the data sheet has **17 columns**, including **Exercise Pages Start**, **Exercise Pages End**, and **Content from PDF** (auto-filled from extracted text when possible).

If you already had an **older 14-column** sheet, run **Startwell → Add detail columns (if sheet is old)** once in the spreadsheet (or redeploy and let the app save again — `getData` migrates automatically).
