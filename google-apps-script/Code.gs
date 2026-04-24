/**
 * Fee voucher web app — bind this script to your Google Sheet (Extensions > Apps Script),
 * or set Script property SPREADSHEET_ID to the sheet ID.
 *
 * Expected header row (row 1), column names are case-insensitive:
 *   ENROLL_ID | NAME | PARENT | CLASS_SEC | ROLL_NO | CAMPUS | VOUCHER_ID |
 *   FEE_SUBTOTAL | FEE_TOTAL | FEE_AFTER_DUE | VOUCHER_VALIDITY | DUE_DATE |
 *   BANK_NAME | BANK_BRANCH | BANK_ACCOUNT | BANK_ACCOUNT_TITLE | CONTACT (optional) |
 *   FEE_HISTORY_JSON (optional) — JSON string, see buildDefaultFeeHistory() shape.
 *
 * Default data source (override with Script property SPREADSHEET_ID or bind script to another sheet):
 * https://docs.google.com/spreadsheets/d/1bn8kjfynnBP0eJqRpdMMe-C2SgOt4I0oj7_u_R9w4B4/edit
 */
var SHEET_NAME = 'Students';

/** Spreadsheet ID from the URL …/spreadsheets/d/<THIS>/edit */
var DEFAULT_SPREADSHEET_ID = '1bn8kjfynnBP0eJqRpdMMe-C2SgOt4I0oj7_u_R9w4B4';

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Download Student Voucher')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function getSpreadsheet_() {
  var propId = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
  if (propId) {
    return SpreadsheetApp.openById(propId);
  }
  try {
    var active = SpreadsheetApp.getActiveSpreadsheet();
    if (active) {
      return active;
    }
  } catch (ignore) {
    // Standalone script project has no container spreadsheet.
  }
  if (DEFAULT_SPREADSHEET_ID) {
    return SpreadsheetApp.openById(DEFAULT_SPREADSHEET_ID);
  }
  throw new Error('No spreadsheet: set SPREADSHEET_ID or bind this script to a Google Sheet.');
}

/**
 * @param {string} enrollId
 * @return {Object} { ok: true, data: {...} } or { ok: false, error: string }
 */
function getStudentByEnrollId(enrollId) {
  var raw = enrollId == null ? '' : String(enrollId).trim();
  if (!raw) {
    return { ok: false, error: 'Please enter your enroll / roll ID.' };
  }
  var key = raw.toLowerCase();

  var ss;
  try {
    ss = getSpreadsheet_();
  } catch (e) {
    return { ok: false, error: 'Spreadsheet not available. Bind the script to your sheet or set SPREADSHEET_ID.' };
  }

  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.getSheets()[0];
  }

  var range = sheet.getDataRange();
  var values = range.getValues();
  if (values.length < 2) {
    return { ok: false, error: 'No student data in the sheet.' };
  }

  var headers = values[0].map(function (h) {
    return String(h).trim().toLowerCase().replace(/\s+/g, '_');
  });

  function col(name) {
    var idx = headers.indexOf(name.toLowerCase());
    if (idx === -1) {
      idx = headers.indexOf(name.toLowerCase().replace(/_/g, ''));
    }
    return idx;
  }

  var idxEnroll = col('enroll_id');
  if (idxEnroll === -1) {
    idxEnroll = col('roll_id');
  }
  if (idxEnroll === -1) {
    idxEnroll = col('enrollid');
  }
  if (idxEnroll === -1) {
    return { ok: false, error: 'Sheet must have a column ENROLL_ID or ROLL_ID.' };
  }

  var row = null;
  for (var r = 1; r < values.length; r++) {
    var cell = values[r][idxEnroll];
    if (cell == null || String(cell).trim() === '') {
      continue;
    }
    if (String(cell).trim().toLowerCase() === key) {
      row = values[r];
      break;
    }
  }

  if (!row) {
    return { ok: false, error: 'No match for this ID. Check your enroll / roll ID and try again.' };
  }

  function val(cname) {
    var i = col(cname);
    return i === -1 ? '' : row[i];
  }

  var feeHistory = buildDefaultFeeHistory();
  var jsonCol = col('fee_history_json');
  if (jsonCol !== -1 && row[jsonCol]) {
    try {
      var parsed = JSON.parse(String(row[jsonCol]));
      if (parsed && typeof parsed === 'object') {
        feeHistory = normalizeFeeHistory_(parsed);
      }
    } catch (ignore) {
      // keep default
    }
  }

  var data = {
    name: String(val('name')),
    parent: String(val('parent')),
    classSec: String(val('class_sec')),
    rollNo: String(val('roll_no')),
    campus: String(val('campus')),
    voucherId: String(val('voucher_id')),
    feeSubtotal: formatMoney_(val('fee_subtotal')),
    feeTotal: formatMoney_(val('fee_total')),
    feeAfterDue: formatMoney_(val('fee_after_due')),
    voucherValidity: formatDateCell_(val('voucher_validity')),
    dueDate: formatDateCell_(val('due_date')),
    contact: String(val('contact')),
    bankName: String(val('bank_name')) || 'MEEZAN BANK',
    bankBranch: String(val('bank_branch')) || 'Bhimber Branch',
    bankAccount: String(val('bank_account')) || 'PK34MEZN0012930105777705',
    bankAccountTitle: String(val('bank_account_title')) || 'ALI HUSSNAIN',
    barcodeValue: String(val('barcode_value') || val('voucher_id') || raw),
    feeHistory: feeHistory,
  };

  return { ok: true, data: data };
}

function formatMoney_(v) {
  if (v === '' || v == null) {
    return '0';
  }
  if (typeof v === 'number') {
    return String(v);
  }
  return String(v).trim();
}

function formatDateCell_(v) {
  if (v instanceof Date) {
    return Utilities.formatDate(v, Session.getScriptTimeZone(), 'dd-MMM-yyyy');
  }
  return v == null ? '' : String(v).trim();
}

/**
 * Default 24 months: 2026 (Apr→Jan) + 2025 (Dec→May) to match typical voucher layout.
 */
function buildDefaultFeeHistory() {
  var months2026 = ['Apr', 'Mar', 'Feb', 'Jan'];
  var months2025 = ['Dec', 'Nov', 'Oct', 'Sep', 'Aug', 'Jul', 'Jun', 'May'];
  var out = [];
  var i;
  for (i = 0; i < months2026.length; i++) {
    out.push({ year: 2026, month: months2026[i], total: 0, paid: 0 });
  }
  for (i = 0; i < months2025.length; i++) {
    out.push({ year: 2025, month: months2025[i], total: 0, paid: 0 });
  }
  return out;
}

/**
 * Accepts { "2026": { "Apr": { "total": 1, "paid": 1 }, ... }, "2025": { ... } }
 * or array of { year, month, total, paid }.
 */
function normalizeFeeHistory_(parsed) {
  if (Array.isArray(parsed)) {
    return parsed.map(function (m) {
      return {
        year: Number(m.year) || 2026,
        month: String(m.month || ''),
        total: Number(m.total) || 0,
        paid: Number(m.paid) || 0,
      };
    });
  }
  var def = buildDefaultFeeHistory();
  for (var i = 0; i < def.length; i++) {
    var slot = def[i];
    var y = parsed[String(slot.year)];
    if (!y || typeof y !== 'object') {
      continue;
    }
    var cell = y[slot.month];
    if (cell && typeof cell === 'object') {
      slot.total = Number(cell.total) || 0;
      slot.paid = Number(cell.paid) || 0;
    }
  }
  return def;
}
