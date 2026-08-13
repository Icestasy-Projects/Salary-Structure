let cancelRequested = false;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SEND_EMAILS") {
    cancelRequested = false;
    handleSendEmails(message.payload)
      .then(result => safeSendMessage({ type: "CAMPAIGN_DONE", result }))
      .catch(err => safeSendMessage({ type: "CAMPAIGN_DONE", result: { success: 0, failed: 0, error: err.message } }));
    sendResponse({ ack: true });
    return false;
  }

  if (message.type === "CANCEL_CAMPAIGN") {
    cancelRequested = true;
    sendResponse({ ack: true });
    return false;
  }
});

async function handleSendEmails({ settings, recipients, subject, body, delay }) {
  const results = { success: 0, failed: 0, errors: [] };
  const zohoDomain = settings.zohoDomain || "zoho.in";

  for (let i = 0; i < recipients.length; i++) {
    if (cancelRequested) {
      safeSendMessage({ type: "PROGRESS", current: i, total: recipients.length, status: "cancelled" });
      break;
    }

    const recipient = recipients[i];
    try {
      await sendViaZoho(settings, recipient, subject, body, zohoDomain);
      results.success++;
      safeSendMessage({
        type: "PROGRESS",
        current: i + 1,
        total: recipients.length,
        name: recipient.name,
        email: recipient.email,
        status: "success"
      });
    } catch (err) {
      results.failed++;
      results.errors.push({ email: recipient.email, error: err.message });
      safeSendMessage({
        type: "PROGRESS",
        current: i + 1,
        total: recipients.length,
        name: recipient.name,
        email: recipient.email,
        status: "failed",
        error: err.message
      });
    }

    if (i < recipients.length - 1 && !cancelRequested) {
      await sleep(delay * 1000);
    }
  }

  return results;
}

async function sendViaZoho(settings, recipient, subjectTemplate, bodyTemplate, zohoDomain) {
  const personalizedSubject = subjectTemplate
    .replace(/\{\{name\}\}/gi, recipient.name || "Sir/Madam")
    .replace(/\{\{company\}\}/gi, recipient.company || "");

  const personalizedBody = bodyTemplate
    .replace(/\{\{name\}\}/gi, recipient.name || "Sir/Madam")
    .replace(/\{\{company\}\}/gi, recipient.company || "");

  const htmlBody = personalizedBody.replace(/\n/g, "<br>");

  const url = "https://mail." + zohoDomain + "/api/accounts/" + settings.accountId + "/messages";

  const payload = {
    fromAddress: settings.email,
    toAddress: recipient.email,
    subject: personalizedSubject,
    content: htmlBody,
    mailFormat: "html"
  };

  if (settings.bcc && settings.bcc.trim()) {
    payload.bccAddress = settings.bcc.trim();
  }

  let response;
  let retries = 0;
  const maxRetries = 2;

  while (retries <= maxRetries) {
    response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": "Zoho-oauthtoken " + settings.accessToken,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (response.status === 429 && retries < maxRetries) {
      retries++;
      const waitTime = retries * 5000;
      safeSendMessage({ type: "PROGRESS", status: "rate_limited", wait: waitTime / 1000, email: recipient.email });
      await sleep(waitTime);
      continue;
    }
    break;
  }

  if (!response.ok) {
    let errorMsg = "HTTP " + response.status;
    try {
      const err = await response.json();
      if (err.data && err.data.errorMessage) {
        errorMsg = err.data.errorMessage;
      } else if (err.data && err.data.moreInfo) {
        errorMsg = err.data.moreInfo;
      }
    } catch (_) {}

    if (response.status === 401) {
      throw new Error("Token expired or invalid. Please regenerate your access token in Settings.");
    }
    throw new Error(errorMsg);
  }
}

function safeSendMessage(msg) {
  try {
    chrome.runtime.sendMessage(msg).catch(() => {});
  } catch (_) {}
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
