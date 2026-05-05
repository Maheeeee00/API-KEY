# Book syllabus designer

Single-page HTML app to keep PDF book links (or local files), read PDFs in the browser with [PDF.js](https://mozilla.github.io/pdf.js/), extract text when the PDF has a text layer, and outline a syllabus per book.

## Run locally

Serve the folder over HTTP (needed for ES modules), for example:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080/index.html`.

**All pages (visual):** toolbar button that draws every page as an image so Urdu/English look exactly as in the PDF (ignores a broken text layer). Large books can be slow; zoom may prompt to re-draw.

## Limits

- **Cross-origin URLs**: Many hosts do not allow browsers to fetch PDFs from another origin (CORS). If loading by URL fails, download the PDF and use **Open local PDF**.
- **Scanned books**: Use **Scan page / Scan all pages (OCR)** in the app for image-only PDFs, or use another desktop OCR tool for highest accuracy.

Data is stored in **localStorage** in this browser (library + outlines). Use **Export JSON** to back up a syllabus.

## ConvertAPI (optional PDF→TXT)

- Paste your **[ConvertAPI token](https://www.convertapi.com/a/authentication)** (Bearer auth — **never** commit tokens in HTML files). The app stores it only in **localStorage** on your machine.
- **ConvertAPI PDF→TXT** uploads the **whole open PDF** via `POST https://v2.convertapi.com/convert/pdf/to/txt` with **OcrMode** auto / never / force.
- If the browser shows **Failed to fetch**, ConvertAPI may block **cross-origin** browser calls for your account — use their docs or a tiny **server proxy** instead.

## Scan (OCR)

- **Scan page** / **Scan all pages** run **Tesseract.js** in the browser (toolbar **OCR langs**: Urdu+English, Arabic+Urdu+English, or English only). Language files load from GitHub (`naptha/tessdata` `4.0.0`, gzipped); first run downloads them.
- **Urdu Nastaliq** is difficult for Tesseract; try **Arabic + Urdu + English**, zoom the PDF before scanning, or use **desktop OCR** (Adobe Acrobat, ABBYY, or Google Drive → open PDF with Google Docs) for production-quality Urdu.

## Extractor (Urdu + Word)

- After each extract, direction is chosen automatically: **Arabic/Urdu script → RTL**, mostly **Latin → LTR**. Use **Force RTL** to override; toggling it stops auto-updates until the next placeholder message clears.
- **RTL** display: if **`DimaMitra.ttf`** sits next to `index.html`, the app prefers **`Dima Mitra `** (trailing space, same as many Swift `custom` names) and **`Dima Mitra`**, then Jameel/Noto. **LTR** uses a clean system sans stack.
- **Download Word (.docx)**: when RTL, requests **`Dima Mitra `** (install the font so Word matches). When LTR, **Calibri**.
- If extracted text shows **random Latin/CJK symbols or �**, the PDF’s **text mapping is wrong** — no font change fixes that; try another PDF or OCR.

