/**
 * WordPress Contact Form Handler
 *
 * SETUP (one-time):
 * 1. Open your Google Sheet → Extensions → Apps Script
 * 2. Paste this entire file + appsscript.json, save
 * 3. Run setupSheet() once (authorize when prompted)
 * 4. Run testEmail() to verify email delivery
 * 5. Deploy → New deployment → Web app
 *    - Execute as: Me (USER_DEPLOYING)
 *    - Who has access: Anyone (ANYONE_ANONYMOUS)
 * 6. Copy the NEW /exec URL into your WordPress form (SCRIPT_URL)
 */

const CONFIG = {
  RECIPIENT_EMAIL: 'maas@airportpasses.com',
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

    try {
      const status = sendNotificationEmail(name, email, phone, subject, message);
      updateEmailStatus(row, status);
    } catch (mailErr) {
      const errorText = String(mailErr);
      updateEmailStatus(row, 'Failed: ' + errorText);
      Logger.log('Email error: ' + errorText);
      return jsonResponse({
        status: 'error',
        message: 'Saved to sheet but email failed: ' + errorText,
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
    sender: getSenderEmail(),
    spreadsheetId: CONFIG.SPREADSHEET_ID,
  });
}

function setupSheet() {
  const sheet = getOrCreateSheet();
  ensureHeaders(sheet);
  sheet.autoResizeColumns(1, HEADERS.length);
  Logger.log('Sheet ready: ' + sheet.getName());
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
  const sheet = getOrCreateSheet();
  sheet.getRange(row, HEADERS.length).setValue(status);
}

function sendNotificationEmail(name, email, phone, subject, message) {
  const emailSubject = 'Contact Form: ' + (subject || 'New Submission');
  const plainBody = buildPlainEmailBody(name, email, phone, subject, message);
  const htmlBody = buildHtmlEmailBody(name, email, phone, subject, message);
  const errors = [];

  // Try simplest send first — complex options often cause "unknown error" in Apps Script.
  const attempts = [
    function() {
      MailApp.sendEmail(CONFIG.RECIPIENT_EMAIL, emailSubject, plainBody);
    },
    function() {
      GmailApp.sendEmail(CONFIG.RECIPIENT_EMAIL, emailSubject, plainBody);
    },
    function() {
      MailApp.sendEmail({
        to: CONFIG.RECIPIENT_EMAIL,
        subject: emailSubject,
        body: plainBody,
        htmlBody: htmlBody,
      });
    },
    function() {
      const options = { htmlBody: htmlBody, name: 'Website Contact Form' };
      if (isValidEmail(email)) {
        options.replyTo = email;
      }
      GmailApp.sendEmail(CONFIG.RECIPIENT_EMAIL, emailSubject, plainBody, options);
    },
  ];

  for (var i = 0; i < attempts.length; i++) {
    try {
      attempts[i]();
      return 'Sent to ' + CONFIG.RECIPIENT_EMAIL;
    } catch (err) {
      var msg = 'Attempt ' + (i + 1) + ': ' + err;
      errors.push(msg);
      Logger.log(msg);
    }
  }

  throw new Error(errors.join(' | '));
}

function buildPlainEmailBody(name, email, phone, subject, message) {
  return [
    'New website contact form submission',
    '',
    'Name:    ' + name,
    'Email:   ' + email,
    'Phone:   ' + (phone || 'Not provided'),
    'Subject: ' + (subject || 'Not provided'),
    '',
    'Message:',
    message || 'No message provided',
    '',
    'Submitted: ' + formatNow(),
    'Sent by Google account: ' + getSenderEmail(),
  ].join('\n');
}

function buildHtmlEmailBody(name, email, phone, subject, message) {
  return [
    '<div style="font-family:Arial,sans-serif;color:#333;max-width:600px;">',
    '<h2 style="color:#1794CC;">New Contact Form Submission</h2>',
    '<table style="width:100%;border-collapse:collapse;">',
    rowHtml('Name', name),
    rowHtml('Email', email),
    rowHtml('Phone', phone || 'Not provided'),
    rowHtml('Subject', subject || 'Not provided'),
    '</table>',
    '<p><strong>Message:</strong></p>',
    '<div style="background:#f5f5f5;padding:15px;border-radius:8px;white-space:pre-wrap;">',
    escapeHtml(message || 'No message provided'),
    '</div>',
    '<p style="color:#777;font-size:12px;">Submitted: ' + formatNow() + '</p>',
    '</div>',
  ].join('');
}

function rowHtml(label, value) {
  return '<tr><td style="padding:8px 0;font-weight:bold;width:100px;">'
    + label + ':</td><td style="padding:8px 0;">' + escapeHtml(value) + '</td></tr>';
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatNow() {
  return Utilities.formatDate(
    new Date(),
    Session.getScriptTimeZone() || 'Asia/Karachi',
    'yyyy-MM-dd HH:mm:ss'
  );
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function getSenderEmail() {
  try {
    return Session.getActiveUser().getEmail() || GmailApp.getUserEmail();
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

  const existing = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  if (existing[0] !== 'Timestamp') {
    sheet.insertRowBefore(1);
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
    return;
  }

  if (existing.length < HEADERS.length || existing[HEADERS.length - 1] !== 'Email Status') {
    sheet.getRange(1, HEADERS.length).setValue('Email Status').setFontWeight('bold');
  }
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/** Run first — sends the simplest possible email to test delivery. */
function testMailSimple() {
  try {
    MailApp.sendEmail(
      CONFIG.RECIPIENT_EMAIL,
      'Simple Test Email',
      'If you receive this, basic mail delivery works for ' + CONFIG.RECIPIENT_EMAIL
    );
    Logger.log('Simple test sent to ' + CONFIG.RECIPIENT_EMAIL);
  } catch (err) {
    Logger.log('Simple test FAILED: ' + err);
    throw err;
  }
}

/** Run from Apps Script editor to test full email template. */
function testEmail() {
  try {
    const status = sendNotificationEmail(
      'Test User',
      'test@example.com',
      '03001234567',
      'Email Test',
      'If you receive this email, the contact form mail is working.'
    );
    Logger.log(status);
    Logger.log('Check inbox and spam for: ' + CONFIG.RECIPIENT_EMAIL);
  } catch (err) {
    Logger.log('testEmail FAILED: ' + err);
    throw err;
  }
}

/** Run from Apps Script editor to test full form flow. */
function testSubmission() {
  const result = doPost({
    postData: {
      contents: JSON.stringify({
        name: 'Test User',
        email: 'test@example.com',
        phone: '03001234567',
        subject: 'Test',
        message: 'This is a test from Apps Script editor.',
      }),
    },
  }).getContent();

  Logger.log(result);
}
