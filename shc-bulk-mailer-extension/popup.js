let recipients = [];
let sent = 0;
let failed = 0;
let campaignRunning = false;

// ── Tab switching ──
function showTab(name) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  const btn = document.getElementById('tabBtn-' + name);
  if (btn) btn.classList.add('active');
}

// ── Recipients ──
function addRecipient() {
  const name    = document.getElementById('addName').value.trim();
  const email   = document.getElementById('addEmail').value.trim().toLowerCase();
  const company = document.getElementById('addCompany').value.trim();

  if (!isValidEmail(email)) {
    alert('Please enter a valid email address.');
    return;
  }

  if (isDuplicate(email)) {
    alert('This email is already in the list.');
    return;
  }

  recipients.push({ name: name || 'Sir/Madam', email, company });
  document.getElementById('addName').value    = '';
  document.getElementById('addEmail').value   = '';
  document.getElementById('addCompany').value = '';
  renderList();
  persistRecipients();
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isDuplicate(email) {
  return recipients.some(r => r.email.toLowerCase() === email.toLowerCase());
}

function removeRecipient(i) {
  recipients.splice(i, 1);
  renderList();
  persistRecipients();
}

function clearAll() {
  if (confirm('Clear all recipients?')) {
    recipients = [];
    renderList();
    persistRecipients();
  }
}

function renderList() {
  const list = document.getElementById('recipientList');
  list.innerHTML = recipients.map((r, i) => `
    <div class="recipient-row">
      <span class="name">${esc(r.name)}</span>
      <span class="email">${esc(r.email)}</span>
      <span class="company">${esc(r.company || '—')}</span>
      <button class="r-del" data-index="${i}">×</button>
    </div>
  `).join('');

  list.querySelectorAll('.r-del').forEach(btn => {
    btn.addEventListener('click', () => removeRecipient(Number(btn.dataset.index)));
  });

  document.getElementById('countBadge').textContent = recipients.length + ' added';
  document.getElementById('recipientCount').value =
    recipients.length + ' recipient' + (recipients.length !== 1 ? 's' : '');
}

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function persistRecipients() {
  chrome.storage.local.set({ recipients });
}

// ── CSV helpers ──
function parseCSVText() {
  const raw = document.getElementById('csvInput').value.trim();
  if (!raw) return;

  const lines = raw.split('\n').map(l => l.trim()).filter(l => l);
  let added = 0;
  let skipped = 0;

  const startIdx = isHeaderRow(lines[0]) ? 1 : 0;

  for (let i = startIdx; i < lines.length; i++) {
    const parts = parseCSVLine(lines[i]);
    if (parts.length < 2) continue;

    const emailIdx = parts.findIndex(p => isValidEmail(p.trim()));
    if (emailIdx === -1) continue;

    const email = parts[emailIdx].trim().toLowerCase();
    if (isDuplicate(email)) { skipped++; continue; }

    const nameParts = parts.filter((_, idx) => idx !== emailIdx);
    const name = nameParts[0] ? nameParts[0].trim() : 'Sir/Madam';
    const company = nameParts[1] ? nameParts[1].trim() : '';

    recipients.push({ name: name || 'Sir/Madam', email, company });
    added++;
  }

  document.getElementById('csvInput').value = '';
  renderList();
  persistRecipients();

  let msg = added + ' recipient' + (added !== 1 ? 's' : '') + ' added.';
  if (skipped) msg += ' ' + skipped + ' duplicate' + (skipped !== 1 ? 's' : '') + ' skipped.';
  alert(msg);
}

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  line = line.replace(/^﻿/, '');

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"' && line[i + 1] === '"') {
        current += '"';
        i++;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        current += ch;
      }
    } else {
      if (ch === '"') {
        inQuotes = true;
      } else if (ch === ',') {
        result.push(current);
        current = '';
      } else {
        current += ch;
      }
    }
  }
  result.push(current);
  return result;
}

function isHeaderRow(line) {
  if (!line) return false;
  const lower = line.toLowerCase();
  return lower.includes('name') && (lower.includes('email') || lower.includes('mail'));
}

function pasteCSV() {
  showTab('recipients');
  document.getElementById('csvInput').focus();
}

function importFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  if (!file.name.endsWith('.csv')) {
    alert('Please use a .csv file.\n\nTo convert from Excel: Open in Excel → File → Save As → choose "CSV (Comma delimited)" format.');
    event.target.value = '';
    return;
  }

  const reader = new FileReader();
  reader.onload = e => {
    const text = e.target.result.replace(/^﻿/, '');
    const lines = text.split(/\r?\n/).map(l => l.trim()).filter(l => l);
    let added = 0;
    let skipped = 0;

    const startIdx = isHeaderRow(lines[0]) ? 1 : 0;

    for (let i = startIdx; i < lines.length; i++) {
      const parts = parseCSVLine(lines[i]);
      if (parts.length < 2) continue;

      const emailIdx = parts.findIndex(p => isValidEmail(p.trim()));
      if (emailIdx === -1) continue;

      const email = parts[emailIdx].trim().toLowerCase();
      if (isDuplicate(email)) { skipped++; continue; }

      const nameParts = parts.filter((_, idx) => idx !== emailIdx);
      const name = nameParts[0] ? nameParts[0].trim() : 'Sir/Madam';
      const company = nameParts[1] ? nameParts[1].trim() : '';

      recipients.push({ name: name || 'Sir/Madam', email, company });
      added++;
    }

    renderList();
    persistRecipients();

    let msg = added + ' recipient' + (added !== 1 ? 's' : '') + ' imported.';
    if (skipped) msg += ' ' + skipped + ' duplicate' + (skipped !== 1 ? 's' : '') + ' skipped.';
    alert(msg);
  };
  reader.readAsText(file);
  event.target.value = '';
}

// ── Settings ──
function saveSettings() {
  const settings = {
    email:       document.getElementById('sEmail').value.trim(),
    accessToken: document.getElementById('sToken').value.trim(),
    accountId:   document.getElementById('sAccountId').value.trim(),
    bcc:         document.getElementById('sBcc').value.trim(),
    zohoDomain:  document.getElementById('sZohoDomain').value
  };

  if (!settings.email || !isValidEmail(settings.email)) {
    alert('Please enter a valid Zoho email address.');
    return;
  }
  if (!settings.accessToken) {
    alert('Please enter your Zoho OAuth access token.');
    return;
  }
  if (!settings.accountId) {
    alert('Please enter your Zoho Account ID.');
    return;
  }

  chrome.storage.local.set({ settings }, () => {
    const badge = document.getElementById('savedBadge');
    badge.style.display = 'inline-block';
    setTimeout(() => { badge.style.display = 'none'; }, 2500);
  });
}

function loadSettings() {
  chrome.storage.local.get(['settings', 'recipients', 'draft'], data => {
    if (data.settings) {
      document.getElementById('sEmail').value       = data.settings.email       || '';
      document.getElementById('sToken').value       = data.settings.accessToken || '';
      document.getElementById('sAccountId').value   = data.settings.accountId   || '';
      document.getElementById('sBcc').value         = data.settings.bcc         || '';
      document.getElementById('sZohoDomain').value  = data.settings.zohoDomain  || 'zoho.in';
    }
    if (data.recipients && data.recipients.length) {
      recipients = data.recipients;
      renderList();
    }
    if (data.draft) {
      if (data.draft.subject) document.getElementById('subject').value = data.draft.subject;
      if (data.draft.body) document.getElementById('body').value = data.draft.body;
    }
  });
}

// ── Draft persistence ──
function saveDraft() {
  const draft = {
    subject: document.getElementById('subject').value,
    body:    document.getElementById('body').value
  };
  chrome.storage.local.set({ draft });
}

// ── Send campaign ──
function startSend() {
  if (recipients.length === 0) {
    alert('Please add at least one recipient first.');
    return;
  }

  chrome.storage.local.get('settings', data => {
    const settings = data.settings || {};
    if (!settings.email || !settings.accessToken || !settings.accountId) {
      alert('Please complete your Zoho settings first (go to Settings tab).');
      return;
    }

    const subject = document.getElementById('subject').value.trim();
    const body    = document.getElementById('body').value.trim();
    const delay   = parseInt(document.getElementById('delay').value);

    if (!subject) { alert('Please enter a subject line.'); return; }
    if (!body)    { alert('Please enter the email body.'); return; }

    const confirmMsg = 'Ready to send ' + recipients.length + ' email' +
      (recipients.length !== 1 ? 's' : '') + '?\n\nFrom: ' + settings.email +
      '\nDelay: ' + delay + 's between emails' +
      (settings.bcc ? '\nBCC: ' + settings.bcc : '');

    if (!confirm(confirmMsg)) return;

    saveDraft();
    campaignRunning = true;
    showProgress(recipients.length);

    chrome.runtime.sendMessage(
      { type: 'SEND_EMAILS', payload: { settings, recipients, subject, body, delay } }
    );
  });
}

function stopCampaign() {
  chrome.runtime.sendMessage({ type: 'CANCEL_CAMPAIGN' });
  addLog('Cancellation requested...', 'info');
  document.getElementById('stopBtn').disabled = true;
}

// ── Progress UI ──
function showProgress(total) {
  sent = 0; failed = 0;
  document.querySelectorAll('.tabs, .panel').forEach(el => el.style.display = 'none');
  const ps = document.getElementById('progressSection');
  ps.style.display = 'block';
  document.getElementById('statTotal').textContent    = total;
  document.getElementById('statSent').textContent     = '0';
  document.getElementById('statFailed').textContent   = '0';
  document.getElementById('progressFill').style.width = '0%';
  document.getElementById('logArea').innerHTML        = '';
  document.getElementById('stopBtn').disabled         = false;
  document.getElementById('stopBtn').style.display    = 'inline-flex';
  document.getElementById('resetBtn').style.display   = 'none';
}

function finishCampaign() {
  campaignRunning = false;
  document.getElementById('stopBtn').style.display  = 'none';
  document.getElementById('resetBtn').style.display = 'inline-flex';
}

function resetUI() {
  document.getElementById('progressSection').style.display = 'none';
  document.querySelector('.tabs').style.display = 'flex';
  document.querySelectorAll('.panel').forEach(p => { p.style.display = ''; });
  showTab('compose');
}

function addLog(msg, type) {
  const log  = document.getElementById('logArea');
  const div  = document.createElement('div');
  div.className = type === 'ok' ? 'log-ok' : type === 'err' ? 'log-err' : 'log-info';
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  div.textContent = '[' + time + '] ' + msg;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

// ── Runtime message listener ──
chrome.runtime.onMessage.addListener(msg => {
  if (msg.type === 'PROGRESS') {
    const total = parseInt(document.getElementById('statTotal').textContent) || recipients.length;

    if (msg.status === 'success') {
      sent++;
      addLog('Sent to ' + msg.name + ' (' + msg.email + ')', 'ok');
    } else if (msg.status === 'failed') {
      failed++;
      addLog('Failed: ' + msg.name + ' (' + msg.email + ') — ' + msg.error, 'err');
    } else if (msg.status === 'rate_limited') {
      addLog('Rate limited. Waiting ' + msg.wait + 's before retrying ' + msg.email + '...', 'info');
      return;
    } else if (msg.status === 'cancelled') {
      addLog('Campaign cancelled by user.', 'info');
      document.getElementById('progressStatus').textContent = 'Cancelled';
      finishCampaign();
      return;
    }

    document.getElementById('statSent').textContent   = sent;
    document.getElementById('statFailed').textContent = failed;
    document.getElementById('progressFill').style.width = (msg.current / total * 100) + '%';
    document.getElementById('progressStatus').textContent = 'Sending ' + msg.current + ' of ' + total + '...';
  }

  if (msg.type === 'CAMPAIGN_DONE') {
    const r = msg.result;
    addLog('Campaign complete: ' + (r.success || 0) + ' sent, ' + (r.failed || 0) + ' failed.', 'info');
    document.getElementById('progressStatus').textContent = 'Done!';
    finishCampaign();
  }
});

// ── Wire up events ──
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => showTab(btn.dataset.tab));
  });

  document.getElementById('sendBtn').addEventListener('click', startSend);
  document.getElementById('addRecipientBtn').addEventListener('click', addRecipient);

  document.getElementById('addEmail').addEventListener('keydown', e => {
    if (e.key === 'Enter') addRecipient();
  });
  document.getElementById('addCompany').addEventListener('keydown', e => {
    if (e.key === 'Enter') addRecipient();
  });

  document.getElementById('importBtn').addEventListener('click', () => {
    document.getElementById('csvFile').click();
  });
  document.getElementById('csvFile').addEventListener('change', importFile);
  document.getElementById('pasteCSVBtn').addEventListener('click', pasteCSV);
  document.getElementById('clearAllBtn').addEventListener('click', clearAll);
  document.getElementById('parseCSVBtn').addEventListener('click', parseCSVText);

  document.getElementById('saveSettingsBtn').addEventListener('click', saveSettings);
  document.getElementById('resetBtn').addEventListener('click', resetUI);
  document.getElementById('stopBtn').addEventListener('click', stopCampaign);

  document.getElementById('subject').addEventListener('input', saveDraft);
  document.getElementById('body').addEventListener('input', saveDraft);

  loadSettings();
});
