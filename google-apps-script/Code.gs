/**
 * Start Well Education — enrollment / voucher row sync
 *
 * SETUP (bound script — recommended)
 * 1. Create or open the Google Spreadsheet that should hold all student rows.
 * 2. Extensions → Apps Script → paste this file → Save.
 * 3. Project Settings → Script properties → add optional:
 *    - API_SECRET : shared secret; HTML form sends the same value as apiSecret.
 *    - SPREADSHEET_ID : only if this script is NOT bound to the spreadsheet (standalone).
 * 4. Deploy → New deployment → Type: Web app
 *    - Execute as: Me
 *    - Who has access: Anyone (or Anyone with Google account, if you prefer)
 * 5. Copy the Web app URL into enroll.html or enroll-config.json (appsScriptWebAppUrl).
 *
 * DEFAULT_SPREADSHEET_ID below matches the shared master sheet when the script runs
 * standalone (no bound spreadsheet). Override with Script property SPREADSHEET_ID.
 *
 * BEHAVIOR
 * - POST JSON: { "action": "saveStudent", "student": { ... }, "spreadsheetId": "optional", "apiSecret": "optional" }
 * - Ensures a master tab "Students" with headers; upserts one row by RollId (case-insensitive).
 * - Creates or replaces a tab named after the roll ID (sanitized) with two columns: Field | Value.
 *
 * NOTE: Browsers on other origins often cannot read the response (CORS). The HTML page uses
 * mode "no-cors" for the POST; success is assumed if the request is sent. Check the Sheet to verify.
 */

/** Master Google Sheet (Start Well). Used when not bound to a spreadsheet. */
var DEFAULT_SPREADSHEET_ID = "1bn8kjfynnBP0eJqRpdMMe-C2SgOt4I0oj7_u_R9w4B4";

var STUDENTS_SHEET_NAME = "Students";
var HEADERS = [
  "RollId",
  "Name",
  "Parent",
  "Class",
  "Section",
  "Campus",
  "Voucher",
  "Subtotal",
  "Total",
  "LateFee",
  "DueDate",
  "VoucherValidity",
];

function spreadsheetUrl_(id) {
  if (!id) {
    return "";
  }
  return "https://docs.google.com/spreadsheets/d/" + id + "/edit";
}

/**
 * Resolves spreadsheet: Script property SPREADSHEET_ID, then POST body spreadsheetId,
 * then DEFAULT_SPREADSHEET_ID, then active spreadsheet if bound.
 * @param {Object} body Parsed POST body (optional).
 */
function getSpreadsheet_(body) {
  body = body || {};
  var props = PropertiesService.getScriptProperties();
  var id = String(props.getProperty("SPREADSHEET_ID") || "").trim();
  if (!id) {
    id = String(body.spreadsheetId || "").trim();
  }
  if (!id && DEFAULT_SPREADSHEET_ID) {
    id = String(DEFAULT_SPREADSHEET_ID).trim();
  }
  if (id) {
    return SpreadsheetApp.openById(id);
  }
  var active = SpreadsheetApp.getActiveSpreadsheet();
  if (!active) {
    throw new Error(
      "No spreadsheet: bind this script to a Sheet, set SPREADSHEET_ID in Script properties, or set DEFAULT_SPREADSHEET_ID in Code.gs."
    );
  }
  return active;
}

function checkApiSecret_(body) {
  var expected = PropertiesService.getScriptProperties().getProperty("API_SECRET");
  if (!expected) {
    return true;
  }
  return String(body.apiSecret || "") === String(expected);
}

function jsonResponse_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function ensureStudentsSheet_(ss) {
  var sh = ss.getSheetByName(STUDENTS_SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(STUDENTS_SHEET_NAME);
  }
  var lastCol = sh.getLastColumn();
  if (lastCol < HEADERS.length) {
    sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  } else {
    var first = sh.getRange(1, 1, 1, HEADERS.length).getValues()[0];
    var empty = true;
    for (var c = 0; c < HEADERS.length; c++) {
      if (String(first[c] || "").trim() !== "") {
        empty = false;
        break;
      }
    }
    if (empty) {
      sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    }
  }
  return sh;
}

function findRowIndexByRollId_(sh, rollId) {
  var want = String(rollId || "")
    .trim()
    .toLowerCase();
  if (!want) {
    return -1;
  }
  var lastRow = sh.getLastRow();
  if (lastRow < 2) {
    return -1;
  }
  var values = sh.getRange(2, 1, lastRow, 1).getValues();
  for (var i = 0; i < values.length; i++) {
    if (String(values[i][0] || "")
      .trim()
      .toLowerCase() === want) {
      return i + 2;
    }
  }
  return -1;
}

function rowFromStudent_(student) {
  return HEADERS.map(function (h) {
    var v = student[h];
    return v != null && v !== undefined ? String(v) : "";
  });
}

function upsertStudentsRow_(sh, student) {
  var roll = String(student.RollId || "").trim();
  if (!roll) {
    throw new Error("student.RollId is required");
  }
  var row = rowFromStudent_(student);
  var rowIndex = findRowIndexByRollId_(sh, roll);
  if (rowIndex < 0) {
    sh.appendRow(row);
    return sh.getLastRow();
  }
  sh.getRange(rowIndex, 1, 1, HEADERS.length).setValues([row]);
  return rowIndex;
}

/** Google Sheet tab names cannot contain : \ / ? * [ ] and max length is 100. */
function detailSheetNameFromRollId_(rollId) {
  var s = String(rollId || "")
    .replace(/[:\\/?*[\]]/g, "_")
    .replace(/\s+/g, " ")
    .trim();
  if (!s) {
    s = "Student";
  }
  if (s.length > 100) {
    s = s.substring(0, 100);
  }
  return s;
}

function syncStudentDetailTab_(ss, student) {
  var name = detailSheetNameFromRollId_(student.RollId);
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
  } else {
    sh.clear();
  }
  var pairs = HEADERS.map(function (h) {
    var v = student[h];
    return [h, v != null && v !== undefined ? String(v) : ""];
  });
  if (pairs.length) {
    sh.getRange(1, 1, pairs.length, 2).setValues(pairs);
  }
  sh.getRange(1, 1, 1, 2).setFontWeight("bold");
  sh.autoResizeColumns(1, 2);
  return name;
}

function doPost(e) {
  try {
    var body = {};
    if (e.postData && e.postData.contents) {
      body = JSON.parse(e.postData.contents);
    } else if (e.parameter && e.parameter.payload) {
      body = JSON.parse(e.parameter.payload);
    }

    if (!checkApiSecret_(body)) {
      return jsonResponse_({ ok: false, error: "Unauthorized" });
    }

    var action = String(body.action || "");
    if (action !== "saveStudent") {
      return jsonResponse_({ ok: false, error: "Unknown action. Use saveStudent." });
    }

    var student = body.student || {};
    var ss = getSpreadsheet_(body);
    var fileId = ss.getId();
    var master = ensureStudentsSheet_(ss);
    upsertStudentsRow_(master, student);
    var detailTab = syncStudentDetailTab_(ss, student);

    return jsonResponse_({
      ok: true,
      message: "Saved",
      spreadsheetId: fileId,
      spreadsheetUrl: spreadsheetUrl_(fileId),
      studentsTab: STUDENTS_SHEET_NAME,
      detailTab: detailTab,
    });
  } catch (err) {
    return jsonResponse_({
      ok: false,
      error: String(err.message || err),
    });
  }
}

/** Optional: open the web app URL in a browser to confirm deployment (returns JSON). */
function doGet() {
  var id = "";
  try {
    id = getSpreadsheet_({}).getId();
  } catch (ignore) {
    id = String(DEFAULT_SPREADSHEET_ID || "").trim();
  }
  return jsonResponse_({
    ok: true,
    hint: "POST JSON with action saveStudent and student object. Optional spreadsheetId in body.",
    studentsTab: STUDENTS_SHEET_NAME,
    spreadsheetId: id || undefined,
    spreadsheetUrl: id ? spreadsheetUrl_(id) : undefined,
  });
}
