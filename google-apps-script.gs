/**
 * Scotland Tree Service — website lead handler
 * ========================================================
 *
 * Receives estimate requests from the website, writes each one as a row in
 * this spreadsheet, and optionally emails you a notification.
 *
 * SETUP — see the "Deliver leads to a Google Sheet" section of README.md
 * for the full walkthrough. In short:
 *
 *   1. Create a Google Sheet.
 *   2. Extensions -> Apps Script. Delete the placeholder code.
 *   3. Paste this whole file in and Save.
 *   4. Set NOTIFY_EMAIL below if you want email alerts.
 *   5. Deploy -> New deployment -> Web app
 *        Execute as:        Me
 *        Who has access:    Anyone
 *   6. Copy the /exec URL it gives you.
 *   7. Paste that URL into SHEET_ENDPOINT in site/script.js.
 *
 * IMPORTANT: after ANY edit to this file you must run
 * Deploy -> Manage deployments -> edit -> Version: New version -> Deploy,
 * or the live site keeps hitting the old code.
 */

/**
 * Leave this as '' if you created the script from inside the sheet
 * (Extensions -> Apps Script). The script is then already bound to it.
 *
 * If you created the script standalone at script.google.com instead, paste
 * the spreadsheet ID here. It is the long string in the sheet's URL between
 * /d/ and /edit:
 *
 *   https://docs.google.com/spreadsheets/d/1AbC...XyZ/edit#gid=0
 *                                          ^^^^^^^^^^^ this part
 */
var SPREADSHEET_ID = '';

/** Tab the leads are written to. Created automatically if missing. */
var SHEET_NAME = 'Leads';

/** Email address for new-lead alerts. Leave as '' to turn alerts off.
 *
 *  Set to tiffindevelopments@gmail.com rather than the domain address, because
 *  info@scotlandtreeservice.com only works once email forwarding is
 *  live at the registrar - and until then alerts would vanish silently while
 *  leads still landed in the sheet.
 *
 *  To switch it later: change this line, then Deploy -> Manage deployments ->
 *  edit -> Version: New version -> Deploy. Saving alone leaves the live site
 *  on the old code. Accepts a comma-separated list for more than one address.
 */
var NOTIFY_EMAIL = 'tiffindevelopments@gmail.com';

/** Column order. Changing this also changes the header row. */
var COLUMNS = [
  ['Received',  function (d) { return new Date(); }],
  ['Name',      function (d) { return d.name    || ''; }],
  ['Phone',     function (d) { return d.phone   || ''; }],
  ['Email',     function (d) { return d.email   || ''; }],
  ['City',      function (d) { return d.city    || ''; }],
  ['Service',   function (d) { return d.service || ''; }],
  ['Message',   function (d) { return d.message || ''; }],
  ['Form',      function (d) { return d.source  || ''; }],
  ['Page URL',  function (d) { return d.pageUrl || ''; }]
];


/**
 * Entry point. The website POSTs JSON here.
 */
function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return reply(false, 'No data received');
    }

    var data = JSON.parse(e.postData.contents);

    // Honeypot: bots fill this in, people never see it.
    if (data.botcheck) {
      return reply(true, 'Discarded');
    }

    // Minimum viable lead. Everything else is optional.
    if (!data.name || !data.phone) {
      return reply(false, 'Name and phone are required');
    }

    appendRow(data);

    if (NOTIFY_EMAIL) {
      sendAlert(data);
    }

    return reply(true, 'Saved');

  } catch (err) {
    // Logged to Apps Script -> Executions so failures are diagnosable
    console.error('Lead handler failed: ' + err);
    return reply(false, String(err));
  }
}


/**
 * Lets you confirm the deployment is live by opening the /exec URL
 * in a browser. Should show a short JSON message.
 */
function doGet() {
  return reply(true, 'Scotland Tree Service lead endpoint is running.');
}


/**
 * Returns the spreadsheet to write to — works whether this script is bound
 * to the sheet or created standalone with SPREADSHEET_ID set.
 */
function getSpreadsheet() {
  if (SPREADSHEET_ID) {
    return SpreadsheetApp.openById(SPREADSHEET_ID);
  }
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) {
    throw new Error(
      'No spreadsheet is bound to this script. Either create the script from ' +
      'inside the sheet (Extensions -> Apps Script), or set SPREADSHEET_ID at ' +
      'the top of this file.');
  }
  return ss;
}


/** Writes one lead, creating the sheet and header row on first use. */
function appendRow(data) {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }

  if (sheet.getLastRow() === 0) {
    var headers = COLUMNS.map(function (c) { return c[0]; });
    sheet.appendRow(headers);
    sheet.getRange(1, 1, 1, headers.length)
         .setFontWeight('bold')
         .setBackground('#1C4430')
         .setFontColor('#ffffff');
    sheet.setFrozenRows(1);
    sheet.setColumnWidth(7, 420);   // give the message column room
  }

  sheet.appendRow(COLUMNS.map(function (c) { return c[1](data); }));
}


/** Emails a readable summary of the lead. */
function sendAlert(data) {
  var lines = [
    'New estimate request from the website.',
    '',
    'Name:     ' + (data.name    || '-'),
    'Phone:    ' + (data.phone   || '-'),
    'Email:    ' + (data.email   || '-'),
    'City:     ' + (data.city    || '-'),
    'Service:  ' + (data.service || '-'),
    '',
    'Message:',
    (data.message || '-'),
    '',
    '---',
    'Submitted from: ' + (data.pageUrl || '-'),
    'Form: ' + (data.source || '-')
  ];

  MailApp.sendEmail({
    to: NOTIFY_EMAIL,
    subject: 'New estimate request: ' + (data.service || 'Scotland Tree Service'),
    body: lines.join('\n'),
    replyTo: data.email || undefined
  });
}


/** Standard JSON response. */
function reply(success, message) {
  return ContentService
    .createTextOutput(JSON.stringify({ success: success, message: message }))
    .setMimeType(ContentService.MimeType.JSON);
}


/**
 * Optional: run this once from the Apps Script editor to confirm the sheet
 * write works before touching the website. Adds one obvious test row.
 */
function testWrite() {
  appendRow({
    name: 'Test Lead',
    phone: '289-000-0000',
    email: 'test@example.com',
    city: 'Scotland',
    service: 'Tree removal',
    message: 'This is a test row. Delete it.',
    source: 'Manual test',
    pageUrl: 'n/a'
  });
}

/**
 * Run this from the editor to test the EMAIL path on its own.
 *
 * testWrite() above only calls appendRow(), so it proves the spreadsheet write
 * and nothing else - sendAlert() is only reached from doPost(), which is the
 * function the website calls. A passing testWrite with no email arriving is
 * therefore the expected result, not a fault.
 *
 * This one sends without touching the sheet. Check the Execution log
 * afterwards: a green "Completed" means Google accepted the message, so if
 * nothing arrives after that the problem is delivery, not the script.
 */
function testAlert() {
  sendAlert({
    name: 'Test Alert',
    phone: '289-000-0000',
    email: 'test@example.com',
    city: 'Scotland',
    service: 'Tree removal',
    message: 'This is a test of the email alert only. No row was written.',
    source: 'Manual email test',
    pageUrl: 'n/a'
  });
  console.log('sendAlert() called. NOTIFY_EMAIL is currently: ' + NOTIFY_EMAIL);
  console.log('Remaining daily email quota: ' + MailApp.getRemainingDailyQuota());
}


/**
 * Run this to check the whole pipeline exactly as the website does it - sheet
 * row and email alert together - without needing the live site. It builds the
 * same JSON payload the form posts and feeds it straight to doPost().
 */
function testFullSubmission() {
  var fake = {
    postData: {
      contents: JSON.stringify({
        name: 'Test Full Submission',
        phone: '289-000-0000',
        email: 'test@example.com',
        city: 'Scotland',
        service: 'Tree removal',
        message: 'End to end test. Delete this row.',
        source: 'Manual full test',
        pageUrl: 'n/a'
      })
    }
  };
  var out = doPost(fake);
  console.log('doPost returned: ' + out.getContent());
}


/**
 * ONE-SHOT DIAGNOSTIC. Run this from the editor if anything is not working.
 *
 * It reports what the script can actually see, rather than what it should be
 * able to see. Read the Execution log underneath after running it.
 *
 * The thing it is really checking is whether this script is BOUND to a
 * spreadsheet. doPost() wraps everything in a try/catch, so when the binding
 * is missing the run still reports "Completed" while silently writing nothing
 * and sending nothing. This function shows you that directly.
 */
function diagnose() {
  var out = [];
  function log(k, v) { out.push(k + ': ' + v); }

  try {
    var ss = getSpreadsheet();
    log('Spreadsheet name', ss.getName());
    log('Spreadsheet URL', ss.getUrl());
    log('Tabs present', ss.getSheets().map(function (s) {
      return s.getName() + ' (' + s.getLastRow() + ' rows)';
    }).join('  |  '));
    var sh = ss.getSheetByName(SHEET_NAME);
    log('Leads tab', sh ? 'exists, ' + sh.getLastRow() + ' rows' : 'DOES NOT EXIST YET');
  } catch (err) {
    log('>>> SPREADSHEET ERROR', String(err));
    log('>>> MEANING', 'This script is not attached to a sheet. Set ' +
                       'SPREADSHEET_ID at the top of this file.');
  }

  log('NOTIFY_EMAIL', NOTIFY_EMAIL || '(empty, alerts are OFF)');
  try {
    log('Remaining daily email quota', MailApp.getRemainingDailyQuota());
  } catch (err) {
    log('>>> MAIL ERROR', String(err));
  }
  try {
    log('Script runs as', Session.getEffectiveUser().getEmail());
  } catch (err) {
    log('User lookup failed', String(err));
  }

  console.log(out.join('\n'));
}
