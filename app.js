(function () {
  "use strict";

  const PDFJS_VERSION = "3.11.174";
  const WORKER_SRC = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${PDFJS_VERSION}/pdf.worker.min.js`;

  if (typeof pdfjsLib !== "undefined") {
    pdfjsLib.GlobalWorkerOptions.workerSrc = WORKER_SRC;
  }

  const ARABIC_BLOCK_START = 0x0600;
  const ARABIC_BLOCK_END = 0x06ff;

  const fileInput = document.getElementById("file-input");
  const dropZone = document.getElementById("drop-zone");
  const statusEl = document.getElementById("status");
  const outputsSection = document.getElementById("outputs");
  const englishOut = document.getElementById("english-output");
  const urduOut = document.getElementById("urdu-output");

  function setStatus(message, type) {
    statusEl.textContent = message || "";
    statusEl.classList.remove("status--error", "status--ok");
    if (type === "error") statusEl.classList.add("status--error");
    if (type === "ok") statusEl.classList.add("status--ok");
  }

  function isInArabicUrduBlock(char) {
    const cp = char.codePointAt(0);
    return cp >= ARABIC_BLOCK_START && cp <= ARABIC_BLOCK_END;
  }

  function isLatinScriptChar(char) {
    return /\p{Script=Latin}/u.test(char);
  }

  /**
   * Arabic block (\u0600-\u06FF) → Urdu box; Latin script → English box.
   * Other characters (spaces, punctuation, digits) follow the preceding script bucket.
   */
  function splitEnglishUrdu(text) {
    let english = "";
    let urdu = "";
    let last = "english";

    for (const char of text) {
      if (isInArabicUrduBlock(char)) {
        urdu += char;
        last = "urdu";
        continue;
      }
      if (isLatinScriptChar(char)) {
        english += char;
        last = "english";
        continue;
      }
      if (last === "urdu") urdu += char;
      else english += char;
    }

    return { english, urdu };
  }

  async function extractTextFromPdf(arrayBuffer) {
    if (typeof pdfjsLib === "undefined") {
      throw new Error("PDF.js failed to load. Check your network connection.");
    }

    const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
    const pdf = await loadingTask.promise;
    const parts = [];

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map((item) => ("str" in item ? item.str : "")).join(" ");
      parts.push(pageText);
    }

    return parts.join("\n\n");
  }

  function showOutputs(english, urdu) {
    englishOut.textContent = english;
    urduOut.textContent = urdu;
    outputsSection.hidden = false;
  }

  async function handleFile(file) {
    if (!file || file.type !== "application/pdf") {
      setStatus("Please choose a PDF file.", "error");
      return;
    }

    setStatus("Processing PDF…", null);
    outputsSection.hidden = true;

    try {
      const buf = await file.arrayBuffer();
      const raw = await extractTextFromPdf(buf);
      const { english, urdu } = splitEnglishUrdu(raw);
      showOutputs(english, urdu);
      setStatus(`Done — extracted from “${file.name}”.`, "ok");
    } catch (err) {
      console.error(err);
      setStatus(err.message || "Could not read this PDF.", "error");
    }
  }

  dropZone.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", () => {
    const file = fileInput.files && fileInput.files[0];
    if (file) handleFile(file);
    fileInput.value = "";
  });

  ["dragenter", "dragover", "dragleave", "drop"].forEach((ev) => {
    dropZone.addEventListener(ev, (e) => {
      e.preventDefault();
      e.stopPropagation();
    });
  });

  dropZone.addEventListener("dragenter", () => dropZone.classList.add("dragover"));
  dropZone.addEventListener("dragover", () => dropZone.classList.add("dragover"));
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
  dropZone.addEventListener("drop", (e) => {
    dropZone.classList.remove("dragover");
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
})();
