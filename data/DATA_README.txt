sallybus-bundle.json — add YOUR real data here (no sample rows are shipped).
============================================================================

{
  "version": 1,
  "curriculum": {
    "Class 8": {
      "Mathematics": [
        {
          "name": "Unit 1: Chapter title",
          "pages": [
            { "label": "Pages 1–10", "topics": ["Topic A", "Topic B"] }
          ]
        }
      ]
    }
  },
  "keybooksByClass": {
    "Class 8": [
      { "title": "English keybook", "file": "data/keybooks/class8-english.pdf" }
    ]
  }
}

Rules:
- Class names must match exactly between curriculum and keybooksByClass.
- "file" is a path relative to the folder that contains sallybus generator.html.
- Put PDFs in data/keybooks/ and reference them as above.

After editing, save the JSON and refresh the browser (F5).
