# SHC Bulk Mailer — Setup & Onboarding Guide

## What This Extension Does

SHC Bulk Mailer is a Chrome browser extension that sends personalized bulk emails through your Zoho Mail account. It is designed for investment outreach — sending deal memos, partnership proposals, and client engagement emails to investors, institutions, and family offices.

Each email is individually sent (not mass BCC) with personalized name and company fields, making them appear as personal 1:1 emails rather than bulk blasts.

---

## Quick Setup (10 minutes)

### Step 1: Install the Extension in Chrome

1. Download and unzip the `shc-bulk-mailer-extension` folder to your computer
2. Open Google Chrome
3. Type `chrome://extensions` in the address bar and press Enter
4. Turn ON **"Developer mode"** — the toggle is in the top-right corner
5. Click the **"Load unpacked"** button
6. Select the `shc-bulk-mailer-extension` folder you unzipped
7. The SHC icon now appears in your Chrome toolbar — click it to open

> **Tip:** If you don't see the icon, click the puzzle-piece icon in Chrome's toolbar and pin "SHC Bulk Mailer".

---

### Step 2: Create a Zoho API Self-Client (One-Time)

You need a Zoho "Self Client" app to authorize the extension to send emails on your behalf.

1. Go to the Zoho API Console:
   - **India:** https://api-console.zoho.in
   - **US/Global:** https://api-console.zoho.com
   - **EU:** https://api-console.zoho.eu
   - **Australia:** https://api-console.zoho.com.au

2. Log in with the same Zoho account you use for email
3. Click **"Add Client"** → select **"Self Client"**
4. Click **"Create Now"**
5. This only needs to be done once — the Self Client stays forever

---

### Step 3: Generate an Access Token

Each access token lasts approximately **1 hour**. You will need to regenerate it before each sending session.

1. In the Zoho API Console, open your **Self Client**
2. Go to the **"Generate Code"** tab
3. In the **Scope** field, enter exactly:
   ```
   ZohoMail.messages.CREATE
   ```
4. Set **Time Duration** to the maximum available
5. Enter any description (e.g., "Bulk mailer")
6. Click **"Generate"**
7. You'll get a **Grant Code** — copy it immediately (it expires in a few minutes)

Now exchange the code for an Access Token:

8. Go to the **"Generate Token"** section (same page)
9. Paste the Grant Code
10. Click **"Generate Token"**
11. Copy the **Access Token** — this is what you enter in the extension

> **Important:** The access token expires after ~1 hour. Before each sending session, repeat steps 2-11 to get a fresh token.

---

### Step 4: Find Your Zoho Account ID

1. Open a new Chrome tab
2. Make sure you are logged into Zoho Mail
3. Visit this URL:
   - **India:** https://mail.zoho.in/api/accounts
   - **US/Global:** https://mail.zoho.com/api/accounts
4. You'll see a JSON response — find the `"accountId"` field
5. Copy that number (e.g., `1234567890123456`)

---

### Step 5: Configure the Extension

1. Click the **SHC Bulk Mailer** icon in Chrome toolbar
2. Go to the **Settings** tab
3. Fill in:
   - **Zoho Region:** Select your Zoho region (India, US, EU, or Australia)
   - **Your Zoho Email:** The email address you send from
   - **Access Token:** Paste the token from Step 3
   - **Account ID:** Paste the number from Step 4
   - **BCC Addresses:** (Optional) Add emails to BCC on every outgoing email, separated by commas
4. Click **"Save Settings"**

You'll see a "Settings saved" confirmation badge appear.

---

## Sending Your First Campaign

### Add Recipients

**Option A — Add one at a time:**
1. Go to the **Recipients** tab
2. Enter Name, Email, and Company (optional)
3. Click the **+** button (or press Enter)

**Option B — Import from CSV file:**
1. Prepare a CSV file with columns: `Name, Email, Company`
2. In the Recipients tab, click **"Import CSV"**
3. Select your CSV file
4. Recipients are loaded automatically (duplicates are skipped)

**Option C — Paste CSV text:**
1. In the Recipients tab, scroll to the text area at the bottom
2. Paste lines in format: `Name, email@example.com, Company Name`
3. Click **"Parse CSV Text"**

> **Note:** Recipients are saved in your browser. They persist across sessions until you clear them.

### Compose Your Email

1. Go to the **Compose** tab
2. Write your **Subject** line
3. Write your **Email Body**
4. Use these personalization tags:
   - `{{name}}` — replaced with each recipient's name
   - `{{company}}` — replaced with each recipient's company
5. Set the **delay between emails** (5-10 seconds recommended to avoid rate limits)

### Send

1. Click **"Send Campaign"**
2. Review the confirmation dialog showing recipient count and settings
3. Confirm to start sending
4. Watch the live progress — sent/failed counts update in real time
5. Each email's status appears in the log area
6. Click **"Stop Campaign"** at any time to cancel remaining emails

---

## CSV File Format

Your CSV file should look like this:

```
Name, Email, Company
John Smith, john@acmecapital.com, Acme Capital
Jane Doe, jane@xyzfamily.com, XYZ Family Office
Raj Patel, raj@abcventures.in, ABC Ventures
```

Rules:
- The first row is treated as a header if it contains "name" and "email" — it will be skipped
- Email column is auto-detected (it looks for the column containing an @ sign)
- Company is optional — leave it blank if not available
- Quoted fields are supported: `"Smith, John", john@example.com, "Acme, Inc."`
- Duplicate emails are automatically skipped

---

## Tips for Outreach

1. **Token refresh:** Regenerate your access token before each session (Step 3)
2. **Delay setting:** Use 5-10 seconds between emails for normal volumes. Use 15-30 seconds for 100+ recipients to avoid Zoho rate limits
3. **Test first:** Add your own email as the only recipient and send a test campaign before the real one
4. **Personalization:** Always use `{{name}}` in the greeting — it makes bulk emails feel personal
5. **BCC tracking:** Add your own email or a shared inbox as BCC in Settings to keep a copy of all outgoing emails
6. **Keep popup open:** The progress display works while the Chrome popup is open. If you close it, emails still send in the background — you just won't see the live progress

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Token expired or invalid" | Generate a new access token (Step 3) and update in Settings |
| Emails failing with HTTP 401 | Same as above — token has expired |
| Emails failing with HTTP 429 | Too many emails too fast — increase the delay between emails |
| Extension not appearing | Go to `chrome://extensions`, ensure it's enabled and Developer Mode is ON |
| No recipients loading from CSV | Ensure your CSV has an email column with @ signs. Check for BOM characters (re-save as UTF-8) |
| "HTTP 400" errors | Check that your Account ID is correct and your email address matches your Zoho account |
| Popup closes while sending | Emails continue in the background. Reopen the popup and send a new campaign to see the UI |

---

## Security Notes

- Your credentials (email, token, account ID) are stored locally in Chrome's extension storage on your computer only
- Credentials are never sent to any server other than Zoho's official API
- Access tokens are short-lived (1 hour) — even if compromised, exposure is limited
- No analytics or tracking is built into this extension
