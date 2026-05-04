// ═══════════════════════════════════════════════════════════════
// STARTWELL EDUCATION — APPS SCRIPT (FINAL VERSION)
// HTML does PDF reading in the browser + structuring via Cursor (paste JSON),
// or an optional OpenAI-compatible API call in the browser.
// Apps Script ONLY saves data to Sheet — no Drive API needed!
// ═══════════════════════════════════════════════════════════════
// SETUP:
//  1. Fill SHEET_ID below
//  2. Run → setupSheet
//  3. Deploy → Web App → Execute as Me → Anyone
// ═══════════════════════════════════════════════════════════════

var SHEET_ID       = "1UU84y90enaHB8SRNxGRbYlkTGU7S8IiSleJp78eooJg";
var DATA_SHEET     = "SyllabusData";
var LOG_SHEET      = "ProcessLog";
var PASSWORD_SHEET = "AdminPasswords";

// ═══════════════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════════════
/** Column count for SyllabusData (after Topics: exercise-level pages + PDF snippet). */
var DATA_NUM_COLS = 17;

function setupSheet() {
  var ss = SpreadsheetApp.openById(SHEET_ID);

  var data = ss.getSheetByName(DATA_SHEET) || ss.insertSheet(DATA_SHEET);
  data.clearContents();
  var h = ["Class","Subject","Book Title","Publisher",
           "Chapter No","Chapter Name","Pages Start","Pages End",
           "Exercise ID","Exercise Label","Exercise Description",
           "Topics","Exercise Pages Start","Exercise Pages End","Content from PDF",
           "Added On","Source File"];
  data.getRange(1,1,1,h.length).setValues([h]);
  _styleHeader(data, h.length);
  data.setFrozenRows(1);
  data.autoResizeColumns(1, h.length);

  var log = ss.getSheetByName(LOG_SHEET) || ss.insertSheet(LOG_SHEET);
  log.clearContents();
  log.getRange(1,1,1,4).setValues([["Timestamp","Action","Details","Status"]]);
  _styleHeader(log, 4);

  var ps = ss.getSheetByName(PASSWORD_SHEET) || ss.insertSheet(PASSWORD_SHEET);
  ps.clearContents();
  ps.getRange(1,1,1,4).setValues([["Username","Display Name","Password","Role"]]);
  _styleHeader(ps, 4);
  ps.appendRow(["admin",   "Administrator", "changeme",   "admin"]);
  ps.appendRow(["teacher", "Teacher",       "teacher123", "teacher"]);
  ps.setFrozenRows(1);
  ps.autoResizeColumns(1,4);

  SpreadsheetApp.getUi().alert(
    "✅ Setup complete!\n\nLogin:\n  admin / changeme\n\n" +
    "Now deploy as Web App:\nDeploy → New deployment → Web App\n" +
    "Execute as: Me | Access: Anyone"
  );
}

function _styleHeader(s, n) {
  s.getRange(1,1,1,n).setBackground("#0f0f1a").setFontColor("#f97316").setFontWeight("bold");
}

// ═══════════════════════════════════════════════════════════════
// WEB APP
// ═══════════════════════════════════════════════════════════════
function doGet(e) {
  var action = (e.parameter && e.parameter.action) || "";
  try {
    if (action === "getData") return _out(getAllData());
    if (action === "ping")    return _out({success:true, message:"Startwell running."});
    return _out({success:false, error:"Unknown action."});
  } catch(err) {
    return _out({success:false, error:err.toString()});
  }
}

function doPost(e) {
  try {
    var b = JSON.parse(e.postData.contents);
    var a = b.action || "";
    if (a === "saveStructured")  return _out(saveStructured(b));
    if (a === "getData")         return _out(getAllData());
    if (a === "deleteEntry")     return _out(deleteEntry(b));
    if (a === "checkPassword")   return _out(checkPassword(b));
    if (a === "changePassword")  return _out(changePassword(b));
    if (a === "addUser")         return _out(addUser(b));
    if (a === "deleteUser")      return _out(deleteUser(b));
    if (a === "getUsers")        return _out(getUsers(b));
    return _out({success:false, error:"Unknown action: "+a});
  } catch(err) {
    _log("ERROR","doPost",err.toString());
    return _out({success:false, error:err.toString()});
  }
}

function _out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/** Upgrade old 14-column sheet: insert exercise page + PDF snippet columns before Added On. Silent when already migrated. */
function ensureDataSheetLayout() {
  var sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(DATA_SHEET);
  if (!sheet || sheet.getLastRow() < 1) return;
  var lastCol = sheet.getLastColumn();
  if (lastCol >= DATA_NUM_COLS) return;
  if (lastCol === 14) {
    sheet.insertColumnsBefore(13, 3);
    sheet.getRange(1, 13, 1, 15).setValues([[
      "Exercise Pages Start", "Exercise Pages End", "Content from PDF"
    ]]);
    _styleHeader(sheet, DATA_NUM_COLS);
  }
}

function migrateDataSheetColumns() {
  ensureDataSheetLayout();
  SpreadsheetApp.getUi().alert("SyllabusData columns checked. If your sheet had 14 columns, three new columns were added before Added On.");
}

// ═══════════════════════════════════════════════════════════════
// SAVE STRUCTURED DATA (sent from browser after PDF.js + structuring)
// No Drive API, no OCR — just save what the browser sends
// ═══════════════════════════════════════════════════════════════
function saveStructured(params) {
  var cls      = (params.className || "").trim();
  var subject  = (params.subject   || "").trim();
  var fileName = (params.fileName  || "upload.pdf").trim();
  var chapters = params.chapters   || [];

  if (!cls)            return {success:false, error:"Class name required."};
  if (!chapters.length) return {success:false, error:"No chapter data received."};

  _log("SAVE","Saving structured data", cls+" | "+subject+" | "+chapters.length+" chapters");

  ensureDataSheetLayout();
  var saved = _saveChapters(chapters, cls, subject, fileName);
  _log("DONE","Saved "+saved+" rows", fileName);

  return {
    success:   true,
    rowsSaved: saved,
    message:   "Saved "+saved+" exercise rows for "+cls+" — "+subject
  };
}

// ═══════════════════════════════════════════════════════════════
// SAVE TO SHEET
// ═══════════════════════════════════════════════════════════════
function _saveChapters(chapters, cls, subject, fileName) {
  var sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(DATA_SHEET);
  var rows  = [], book = "", pub = "", ts = new Date().toLocaleString();

  chapters.forEach(function(ch) {
    if (!book && ch.bookTitle) book = ch.bookTitle;
    if (!pub  && ch.publisher) pub  = ch.publisher;
    (ch.exercises || []).forEach(function(ex) {
      var exPs = ex.pageStart != null && ex.pageStart !== "" ? String(ex.pageStart) : "";
      var exPe = ex.pageEnd != null && ex.pageEnd !== "" ? String(ex.pageEnd) : "";
      var snip = String(ex.contentFromPdf || ex.snippet || "").trim();
      if (snip.length > 4500) snip = snip.substring(0, 4500) + "…";
      rows.push([
        cls, subject, book||fileName, pub||"",
        ch.chapterNo||"", ch.chapterName||"",
        ch.pagesStart||"", ch.pagesEnd||"",
        ex.exerciseId||"", ex.exerciseLabel||"",
        ex.description||"", ex.topics||"",
        exPs, exPe, snip,
        ts, fileName
      ]);
    });
  });

  if (!book) {
    var titles = [];
    chapters.forEach(function(ch) {
      if (ch.bookTitle) titles.push(String(ch.bookTitle).trim());
    });
    if (titles.length) {
      var uniq = {}, order = [];
      titles.forEach(function(t) {
        if (t && !uniq[t]) { uniq[t] = true; order.push(t); }
      });
      book = order.join(" | ");
    }
  }

  if (rows.length) {
    var bFinal = book || fileName;
    for (var r = 0; r < rows.length; r++) rows[r][2] = bFinal;
  }

  if (rows.length) {
    var last = sheet.getLastRow();
    sheet.getRange(last+1, 1, rows.length, DATA_NUM_COLS).setValues(rows);
    for (var i = 0; i < rows.length; i++)
      sheet.getRange(last+1+i, 1, 1, DATA_NUM_COLS)
        .setBackground(i % 2 === 0 ? "#fff8f4" : "#ffffff");
  }
  return rows.length;
}

// ═══════════════════════════════════════════════════════════════
// GET ALL DATA
// ═══════════════════════════════════════════════════════════════
function getAllData() {
  var sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(DATA_SHEET);
  if (!sheet) return {success:false, error:"Run setupSheet first."};
  ensureDataSheetLayout();
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return {success:true, data:{}, rows:[]};

  var lastCol = Math.max(sheet.getLastColumn(), DATA_NUM_COLS);
  var raw = sheet.getRange(2,1,lastRow-1,lastCol).getValues();
  var rows = [], curriculum = {};

  raw.forEach(function(row, idx) {
    var cls=String(row[0]).trim(), subj=String(row[1]).trim(),
        book=String(row[2]).trim(), pub=String(row[3]).trim(),
        chNo=String(row[4]).trim(), chName=String(row[5]).trim(),
        pgS=String(row[6]).trim(), pgE=String(row[7]).trim(),
        exId=String(row[8]).trim(), exLbl=String(row[9]).trim(),
        exDesc=String(row[10]).trim(), topics=String(row[11]).trim(),
        exPgS="", exPgE="", pdfSnip="", addedOn="", src="";
    if (row.length >= 17) {
      exPgS=String(row[12]||"").trim();
      exPgE=String(row[13]||"").trim();
      pdfSnip=String(row[14]||"").trim();
      addedOn=String(row[15]||"").trim();
      src=String(row[16]||"").trim();
    } else {
      addedOn=String(row[12]||"").trim();
      src=String(row[13]||"").trim();
    }
    if (!cls||!chName) return;

    rows.push({rowIndex:idx,cls,subj,book,pub,chNo,chName,pgS,pgE,exId,exLbl,exDesc,topics,exPgS,exPgE,pdfSnip,addedOn,src});
    if (!curriculum[cls]) curriculum[cls]={};
    if (!curriculum[cls][subj]) curriculum[cls][subj]={bookTitle:book,publisher:pub,chapters:{}};
    var chKey=chNo+"|"+chName;
    if (!curriculum[cls][subj].chapters[chKey])
      curriculum[cls][subj].chapters[chKey]={chapterNo:chNo,chapterName:chName,pagesStart:pgS,pagesEnd:pgE,exercises:[]};
    if (exId||exLbl)
      curriculum[cls][subj].chapters[chKey].exercises.push({
        exerciseId:exId,exerciseLabel:exLbl,description:exDesc,topics,
        pageStart:exPgS,pageEnd:exPgE,contentFromPdf:pdfSnip
      });
  });
  return {success:true, data:curriculum, rows};
}

// ═══════════════════════════════════════════════════════════════
// DELETE
// ═══════════════════════════════════════════════════════════════
function deleteEntry(p) {
  var idx=parseInt(p.rowIndex,10);
  if (isNaN(idx)||idx<0) return {success:false,error:"Invalid index."};
  var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(DATA_SHEET);
  var row=idx+2;
  if (row>sheet.getLastRow()) return {success:false,error:"Row not found."};
  sheet.deleteRow(row);
  return {success:true,message:"Deleted."};
}

// ═══════════════════════════════════════════════════════════════
// PASSWORDS
// ═══════════════════════════════════════════════════════════════
function checkPassword(p) {
  var u=String(p.username||"").trim().toLowerCase(), pw=String(p.password||"").trim();
  if (!u||!pw) return {success:false,error:"Username and password required."};
  var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(PASSWORD_SHEET);
  if (!sheet) return {success:false,error:"Run setupSheet first."};
  var last=sheet.getLastRow();
  if (last<2) return {success:false,error:"No accounts found."};
  var rows=sheet.getRange(2,1,last-1,4).getValues();
  for (var i=0;i<rows.length;i++)
    if (String(rows[i][0]).trim().toLowerCase()===u && String(rows[i][2]).trim()===pw)
      return {success:true,username:String(rows[i][0]).trim(),displayName:String(rows[i][1]).trim(),role:String(rows[i][3]).trim()};
  return {success:false,error:"Invalid username or password."};
}

function changePassword(p) {
  var u=String(p.username||"").trim().toLowerCase();
  var op=String(p.oldPassword||"").trim(), np=String(p.newPassword||"").trim();
  if (!u||!op||!np) return {success:false,error:"All fields required."};
  if (np.length<6) return {success:false,error:"Min 6 characters."};
  var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(PASSWORD_SHEET);
  if (!sheet) return {success:false,error:"Sheet not found."};
  var rows=sheet.getRange(2,1,sheet.getLastRow()-1,4).getValues();
  for (var i=0;i<rows.length;i++)
    if (String(rows[i][0]).trim().toLowerCase()===u && String(rows[i][2]).trim()===op) {
      sheet.getRange(2+i,3).setValue(np);
      return {success:true,message:"Password updated."};
    }
  return {success:false,error:"Current password incorrect."};
}

function getUsers(p) {
  if (!_isAdmin(p.callerUsername)) return {success:false,error:"Admin only."};
  var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(PASSWORD_SHEET);
  if (!sheet) return {success:false,error:"Sheet not found."};
  var last=sheet.getLastRow();
  if (last<2) return {success:true,users:[]};
  return {success:true,users:sheet.getRange(2,1,last-1,4).getValues()
    .map(function(r){return {username:String(r[0]).trim(),displayName:String(r[1]).trim(),role:String(r[3]).trim()};})
    .filter(function(u){return u.username;})};
}

function addUser(p) {
  if (!_isAdmin(p.callerUsername)) return {success:false,error:"Admin only."};
  var u=String(p.username||"").trim(), pw=String(p.password||"").trim();
  if (!u||!pw) return {success:false,error:"Username and password required."};
  if (pw.length<6) return {success:false,error:"Min 6 chars."};
  var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(PASSWORD_SHEET);
  if (!sheet) return {success:false,error:"Sheet not found."};
  var last=sheet.getLastRow();
  if (last>=2) {
    var ex=sheet.getRange(2,1,last-1,1).getValues();
    for (var i=0;i<ex.length;i++)
      if (String(ex[i][0]).trim().toLowerCase()===u.toLowerCase())
        return {success:false,error:"Username already exists."};
  }
  sheet.appendRow([u,String(p.displayName||u).trim(),pw,String(p.role||"teacher").trim()]);
  return {success:true,message:"User '"+u+"' added."};
}

function deleteUser(p) {
  if (!_isAdmin(p.callerUsername)) return {success:false,error:"Admin only."};
  var target=String(p.targetUsername||"").trim().toLowerCase();
  if (!target) return {success:false,error:"Target required."};
  if (target===String(p.callerUsername||"").trim().toLowerCase())
    return {success:false,error:"Cannot delete yourself."};
  var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(PASSWORD_SHEET);
  if (!sheet) return {success:false,error:"Sheet not found."};
  var rows=sheet.getRange(2,1,sheet.getLastRow()-1,1).getValues();
  for (var i=0;i<rows.length;i++)
    if (String(rows[i][0]).trim().toLowerCase()===target) {
      sheet.deleteRow(i+2);
      return {success:true,message:"User '"+target+"' deleted."};
    }
  return {success:false,error:"User not found."};
}

function _isAdmin(caller) {
  if (!caller) return false;
  var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(PASSWORD_SHEET);
  if (!sheet||sheet.getLastRow()<2) return false;
  var rows=sheet.getRange(2,1,sheet.getLastRow()-1,4).getValues();
  for (var i=0;i<rows.length;i++)
    if (String(rows[i][0]).trim().toLowerCase()===caller.trim().toLowerCase())
      return String(rows[i][3]).trim()==="admin";
  return false;
}

// ═══════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════
function _log(status, action, details) {
  try {
    var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(LOG_SHEET);
    if (sheet) sheet.appendRow([new Date().toLocaleString(),action,String(details||"").substring(0,500),status]);
  } catch(e) {}
}

function onOpen() {
  SpreadsheetApp.getUi().createMenu("📚 Startwell")
    .addItem("Setup Sheets","setupSheet")
    .addItem("Add detail columns (if sheet is old)","migrateDataSheetColumns")
    .addSeparator()
    .addItem("View Data Count","showDataCount")
    .addItem("Clear All Data","clearAllData")
    .addToUi();
}
function showDataCount() {
  var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(DATA_SHEET);
  SpreadsheetApp.getUi().alert("📊 Rows: "+Math.max(0,(sheet?sheet.getLastRow():1)-1));
}
function clearAllData() {
  var ui=SpreadsheetApp.getUi();
  if (ui.alert("⚠️ Clear ALL?","Cannot be undone.",ui.ButtonSet.YES_NO)===ui.Button.YES) {
    var sheet=SpreadsheetApp.openById(SHEET_ID).getSheetByName(DATA_SHEET);
    if (sheet&&sheet.getLastRow()>1) sheet.deleteRows(2,sheet.getLastRow()-1);
    ui.alert("✅ Cleared.");
  }
}
