# Book syllabus designer

Single-page HTML app to keep PDF book links (or local files), read PDFs in the browser with [PDF.js](https://mozilla.github.io/pdf.js/), extract text when the PDF has a text layer, and outline a syllabus per book.

## Run locally

Serve the folder over HTTP (needed for ES modules), for example:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080/index.html`.

## Limits

- **Cross-origin URLs**: Many hosts do not allow browsers to fetch PDFs from another origin (CORS). If loading by URL fails, download the PDF and use **Open local PDF**.
- **Scanned books**: Text extraction only works when the PDF includes a text layer; image-only pages need OCR in another tool.

Data is stored in **localStorage** in this browser (library + outlines). Use **Export JSON** to back up a syllabus.

## Extractor (Urdu + Word)

- The extractor uses **Jameel Noori Nastaleeq** when that font is installed locally (several common PostScript names are checked).
- **Noto Nastaliq Urdu** is embedded via jsDelivr WOFF2 so Nastaliq shaping works even when Google Fonts is blocked or Jameel is missing.
- If extracted text shows **random Latin/CJK symbols or �**, the PDF’s **text mapping is wrong** — no font change fixes that; try another PDF or OCR.

