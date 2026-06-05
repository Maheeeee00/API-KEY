/**
 * WordPress Contact Form Handler
 *
 * SETUP (one-time):
 * 1. Create a new Google Sheet (e.g. "Contact Form Submissions")
 * 2. Open Extensions → Apps Script
 * 3. Paste this entire file, save
 * 4. Run setupSheet() once (authorize when prompted)
 * 5. Add appsscript.json (Project Settings → "Show appsscript.json manifest file")
 * 6. Deploy → New deployment → Web app
 *    - Execute as: Me (USER_DEPLOYING)
 *    - Who has access: Anyone (ANYONE_ANONYMOUS)
 * 7. Copy the /exec URL into your WordPress form fetch() call
 */

const CONFIG = {
  RECIPIENT_EMAIL: 'hassanofficial@gmail.com',
  SHEET_NAME: 'Submissions',
};

/**
 * Handles POST requests from the WordPress contact form.
 */
function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return jsonResponse({ status: 'error', message: 'No data received' });
    }

    const data = JSON.parse(e.postData.contents);
    const name = (data.name || '').trim();
    const email = (data.email || '').trim();
    const phone = (data.phone || '').trim();
    const subject = (data.subject || '').trim();
    const message = (data.message || '').trim();

    if (!name || !email) {
      return jsonResponse({ status: 'error', message: 'Name and email are required' });
    }

    saveToSheet(name, email, phone, subject, message);
    sendNotificationEmail(name, email, phone, subject, message);

    return jsonResponse({ status: 'success' });
  } catch (err) {
    Logger.log('doPost error: ' + err);
    return jsonResponse({ status: 'error', message: String(err) });
  }
}

/**
 * Health check — open the /exec URL in a browser to verify deployment.
 */
function doGet() {
  return jsonResponse({
    status: 'ok',
    message: 'Contact form endpoint is active',
    recipient: CONFIG.RECIPIENT_EMAIL,
  });
}

/**
 * Run once from the Apps Script editor to create headers.
 */
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
      Session.getScriptTimeZone(),
      'yyyy-MM-dd HH:mm:ss'
    ),
    '',
    'Reply directly to this email to respond to the sender.',
  ].join('\n');

  MailApp.sendEmail({
    to: CONFIG.RECIPIENT_EMAIL,
    subject: emailSubject,
    body: body,
    replyTo: email,
    name: name + ' (via Contact Form)',
  });
}

function getOrCreateSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.SHEET_NAME);
    setupSheet();
  }

  return sheet;
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
