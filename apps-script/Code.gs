/**
 * WordPress Contact Form Handler
 *
 * SETUP (one-time):
 * 1. Open your Google Sheet → Extensions → Apps Script
 * 2. Paste this entire file + appsscript.json, save
 * 3. Run setupSheet() once (authorize when prompted)
 * 4. Deploy → New deployment → Web app
 *    - Execute as: Me (USER_DEPLOYING)
 *    - Who has access: Anyone (ANYONE_ANONYMOUS)
 * 5. Copy the NEW /exec URL into your WordPress form (SCRIPT_URL)
 *
 * If the form shows "Something went wrong", redeploy a new version —
 * an old deployment URL without doPost will always fail.
 */

const CONFIG = {
  RECIPIENT_EMAIL: 'hassanofficial@gmail.com',
  SPREADSHEET_ID: '167qMEH8KXxv_LGE5UzFzVwVp_QSN6bJsCz520aE3t18',
  SHEET_NAME: 'Submissions',
};

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

    saveToSheet(name, email, phone, subject, message);

    try {
      sendNotificationEmail(name, email, phone, subject, message);
    } catch (mailErr) {
      Logger.log('Email error: ' + mailErr);
      return jsonResponse({
        status: 'error',
        message: 'Saved to sheet but email failed: ' + mailErr,
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
    spreadsheetId: CONFIG.SPREADSHEET_ID,
  });
}

function setupSheet() {
  const sheet = getOrCreateSheet();
  const headers = ['Timestamp', 'Name', 'Email', 'Phone', 'Subject', 'Message'];

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, headers.length);
  }

  Logger.log('Sheet ready: ' + sheet.getName());
}

function parseRequestData(e) {
  if (!e) {
    throw new Error('No request data received');
  }

  if (e.postData && e.postData.contents) {
    const contents = e.postData.contents;
    try {
      return JSON.parse(contents);
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

function saveToSheet(name, email, phone, subject, message) {
  const sheet = getOrCreateSheet();
  sheet.appendRow([new Date(), name, email, phone, subject, message]);
}

function sendNotificationEmail(name, email, phone, subject, message) {
  const emailSubject = subject
    ? 'Contact Form: ' + subject
    : 'New Contact Form Submission';

  const body = [
    'You received a new message from your website contact form.',
    '',
    'Name:    ' + name,
    'Email:   ' + email,
    'Phone:   ' + (phone || 'Not provided'),
    'Subject: ' + (subject || 'Not provided'),
    '',
    'Message:',
    '──────────────────────────────',
    message || 'No message provided',
    '──────────────────────────────',
    '',
    'Submitted: ' + Utilities.formatDate(
      new Date(),
      Session.getScriptTimeZone() || 'Asia/Karachi',
      'yyyy-MM-dd HH:mm:ss'
    ),
    '',
    'Reply directly to this email to respond to the sender.',
  ].join('\n');

  const options = {
    to: CONFIG.RECIPIENT_EMAIL,
    subject: emailSubject,
    body: body,
  };

  if (email && email.indexOf('@') > 0) {
    options.replyTo = email;
  }

  MailApp.sendEmail(options);
}

function getSpreadsheet() {
  return SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
}

function getOrCreateSheet() {
  const ss = getSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.SHEET_NAME);
    const headers = ['Timestamp', 'Name', 'Email', 'Phone', 'Subject', 'Message'];
    sheet.appendRow(headers);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }

  return sheet;
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function testSubmission() {
  const mockEvent = {
    postData: {
      contents: JSON.stringify({
        name: 'Test User',
        email: 'test@example.com',
        phone: '03001234567',
        subject: 'Test',
        message: 'This is a test from Apps Script editor.',
      }),
    },
  };

  const result = doPost(mockEvent).getContent();
  Logger.log(result);
}
