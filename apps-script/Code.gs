/**
 * WordPress Contact Form Handler
 *
 * If you see "An unknown error has occurred":
 * 1. Run diagnose() and check Executions log
 * 2. Run testMailSimple() — if it fails, the email address may be wrong
 * 3. Confirm maas@airportpasses.com exists in your hosting/cPanel
 * 4. Re-authorize: Run any function → Review permissions → Allow
 * 5. Redeploy web app after saving changes
 */

const CONFIG = {
  RECIPIENT_EMAIL: 'maas@airportpasses.com',
  BACKUP_EMAIL: 'hassanofficial@gmail.com',
  SPREADSHEET_ID: '167qMEH8KXxv_LGE5UzFzVwVp_QSN6bJsCz520aE3t18',
  SHEET_NAME: 'Submissions',
};

const HEADERS = [
  'Timestamp',
  'Name',
  'Email',
  'Phone',
  'Subject',
  'Message',
  'Email Status',
];

function doPost(e) {
  try {
    const data = parseRequestData(e);
    const name = (data.name || '').trim();
    const email = (data.email || '').trim();
    const phone = (data.phone || '').trim();
    const subject = (data.subject || '').trim();
    const message = (data.message || '').trim();

    if (!name || !email) {
      return jsonResponse({ status: 'error', message: 'Name and email are required' });
    }

    const row = saveToSheet(name, email, phone, subject, message, 'Pending');
    const mailResult = sendNotificationEmail(name, email, phone, subject, message);
    updateEmailStatus(row, mailResult.status);

    if (!mailResult.ok) {
      return jsonResponse({
        status: 'error',
        message: 'Saved to sheet but email failed: ' + mailResult.status,
      });
    }

    return jsonResponse({ status: 'success' });
  } catch (err) {
    Logger.log('doPost error: ' + err);
    return jsonResponse({ status: 'error', message: String(err) });
  }
}

function doGet() {
  return jsonResponse({
    status: 'ok',
    message: 'Contact form endpoint is active',
    recipient: CONFIG.RECIPIENT_EMAIL,
    backup: CONFIG.BACKUP_EMAIL,
    sender: getSenderEmail(),
    spreadsheetId: CONFIG.SPREADSHEET_ID,
  });
}

function setupSheet() {
  const sheet = getOrCreateSheet();
  ensureHeaders(sheet);
  Logger.log('Sheet ready: ' + sheet.getName());
}

function diagnose() {
  const report = {
    sender: getSenderEmail(),
    recipient: CONFIG.RECIPIENT_EMAIL,
    backup: CONFIG.BACKUP_EMAIL,
    sheet: 'unknown',
    backupMail: 'unknown',
    primaryMail: 'unknown',
  };

  try {
    getSpreadsheet().getName();
    report.sheet = 'OK - can access spreadsheet';
  } catch (err) {
    report.sheet = 'FAILED: ' + err;
  }

  try {
    MailApp.sendEmail(
      CONFIG.BACKUP_EMAIL,
      'Diagnose Test',
      'Backup email test at ' + new Date()
    );
    report.backupMail = 'OK - sent to ' + CONFIG.BACKUP_EMAIL;
  } catch (err) {
    report.backupMail = 'FAILED: ' + err;
  }

  try {
    MailApp.sendEmail(
      CONFIG.RECIPIENT_EMAIL,
      'Diagnose Test',
      'Primary email test at ' + new Date()
    );
    report.primaryMail = 'OK - sent to ' + CONFIG.RECIPIENT_EMAIL;
  } catch (err) {
    report.primaryMail = 'FAILED: ' + err;
  }

  Logger.log(JSON.stringify(report, null, 2));
  return report;
}

function testMailSimple() {
  MailApp.sendEmail(
    CONFIG.BACKUP_EMAIL,
    'Simple Test',
    'Basic MailApp test to backup Gmail.'
  );
  Logger.log('Sent simple test to ' + CONFIG.BACKUP_EMAIL);
}

function testEmail() {
  const result = sendNotificationEmail(
    'Test User',
    'test@example.com',
    '03001234567',
    'Email Test',
    'Contact form email test.'
  );
  Logger.log(JSON.stringify(result));
}

function testSubmission() {
  const result = doPost({
    postData: {
      contents: JSON.stringify({
        name: 'Test User',
        email: 'test@example.com',
        phone: '03001234567',
        subject: 'Test',
        message: 'Test from Apps Script editor.',
      }),
    },
  }).getContent();
  Logger.log(result);
}

function parseRequestData(e) {
  if (!e) {
    throw new Error('No request data received');
  }

  if (e.postData && e.postData.contents) {
    try {
      return JSON.parse(e.postData.contents);
    } catch (parseErr) {
      throw new Error('Invalid JSON body: ' + parseErr);
    }
  }

  if (e.parameter) {
    return {
      name: e.parameter.name,
      email: e.parameter.email,
      phone: e.parameter.phone,
      subject: e.parameter.subject,
      message: e.parameter.message,
    };
  }

  throw new Error('No form data received');
}

function saveToSheet(name, email, phone, subject, message, emailStatus) {
  const sheet = getOrCreateSheet();
  ensureHeaders(sheet);
  sheet.appendRow([
    new Date(),
    name,
    email,
    phone,
    subject,
    message,
    emailStatus || 'Pending',
  ]);
  return sheet.getLastRow();
}

function updateEmailStatus(row, status) {
  getOrCreateSheet().getRange(row, HEADERS.length).setValue(status);
}

function sendNotificationEmail(name, email, phone, subject, message) {
  const emailSubject = 'Contact Form: ' + (subject || 'New Submission');
  const body = buildPlainEmailBody(name, email, phone, subject, message);

  var primaryError = trySendMail(CONFIG.RECIPIENT_EMAIL, emailSubject, body);
  if (!primaryError) {
    return { ok: true, status: 'Sent to ' + CONFIG.RECIPIENT_EMAIL };
  }

  Logger.log('Primary email failed: ' + primaryError);

  var backupError = trySendMail(CONFIG.BACKUP_EMAIL, emailSubject, body);
  if (!backupError) {
    return {
      ok: true,
      status: 'Primary failed, sent to backup ' + CONFIG.BACKUP_EMAIL,
    };
  }

  return {
    ok: false,
    status: 'Primary: ' + primaryError + ' | Backup: ' + backupError,
  };
}

function trySendMail(to, subject, body) {
  try {
    MailApp.sendEmail(String(to).trim(), String(subject), String(body));
    return '';
  } catch (err) {
    return String(err);
  }
}

function buildPlainEmailBody(name, email, phone, subject, message) {
  return [
    'New website contact form submission',
    '',
    'Name: ' + name,
    'Email: ' + email,
    'Phone: ' + (phone || 'Not provided'),
    'Subject: ' + (subject || 'Not provided'),
    '',
    'Message:',
    message || 'No message provided',
    '',
    'Submitted: ' + formatNow(),
  ].join('\n');
}

function formatNow() {
  return Utilities.formatDate(
    new Date(),
    Session.getScriptTimeZone() || 'Asia/Karachi',
    'yyyy-MM-dd HH:mm:ss'
  );
}

function getSenderEmail() {
  try {
    return Session.getActiveUser().getEmail() || 'unknown';
  } catch (err) {
    return 'unknown';
  }
}

function getSpreadsheet() {
  return SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
}

function getOrCreateSheet() {
  const ss = getSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.SHEET_NAME);
    ensureHeaders(sheet);
  }

  return sheet;
}

function ensureHeaders(sheet) {
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
    return;
  }

  const firstCell = sheet.getRange(1, 1).getValue();
  if (firstCell !== 'Timestamp') {
    sheet.insertRowBefore(1);
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
    return;
  }

  if (sheet.getLastColumn() < HEADERS.length) {
    sheet.getRange(1, HEADERS.length).setValue('Email Status').setFontWeight('bold');
  }
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
