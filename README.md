# startwell — local syllabus

## Run locally (so `data/curriculum.json` loads)

Browsers block `fetch()` for JSON when you open `index.html` as a `file://` URL. Use any static server from this folder, for example:

```bash
cd /path/to/this/repo
python3 -m http.server 8080
```

Then open **http://localhost:8080/index.html** (or **http://localhost:8080/** if you rename `index.html` to `index.html` in root).

**Offline / local mode** also turns on if you open the file directly (`file://`) or add **`?local=1`** to the URL when using a server.

## Put your syllabus here

1. Export or build curriculum as JSON in the same shape as the sample in **`data/curriculum.json`** (nested `Class` → `Subject` → `chapters` → exercises), or use **`{ "data": { ... }, "rows": [] }`** where `rows` can be empty (they are rebuilt from `data`).
2. Replace **`data/curriculum.json`** with your file (you can merge multiple books by adding more class/subject keys).
3. After editing in the app, use **Admin → Data → Export curriculum.json** and copy the file back into **`data/`** if you want it on disk.

Google Drive folders cannot be read directly from a static page without the Drive API and OAuth. Download PDFs or sheets from Drive, then add structured data to **`data/curriculum.json`** or use the admin PDF + Cursor paste flow.

## Google Sheets mode

Set **`SCRIPT_URL`** in `index.html` to your Apps Script web app URL and open the page **without** `file:` / `?local=1` to use the cloud backend (`Code.gs`).
