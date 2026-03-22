# WhatsApp Business API Setup Guide

Complete guide to get WhatsApp Business API credentials for receiving/sending messages.

---

## 📋 Prerequisites

1. **Facebook Business Account** (Meta Business Suite)
2. **Phone Number** for WhatsApp Business (can be a new number)
3. **Facebook Page** (optional but recommended)

---

## 🚀 Step-by-Step Setup

### Step 1: Go to Meta for Developers

1. Open: https://developers.facebook.com/
2. Click **"Get Started"** or **"Log In"**
3. Login with your Facebook account (urojk77@gmail.com)

---

### Step 2: Create a WhatsApp Business App

1. Click **"My Apps"** (top right)
2. Click **"Create App"**
3. Select use case: **"Other"** → Click **Next**
4. Select app type: **"Business"** → Click **Next**
5. Fill in app details:
   - **App Name:** `AI Employee WhatsApp`
   - **App Contact Email:** `urojk77@gmail.com`
   - Click **"Create App"**

---

### Step 3: Add WhatsApp Product

1. In your new app dashboard, find **"WhatsApp"** product
2. Click **"Set Up"** next to WhatsApp
3. This will add WhatsApp Business API to your app

---

### Step 4: Get Your Phone Number ID

#### Option A: Add a Phone Number Now

1. Go to **WhatsApp → API Setup** in left menu
2. Under **"Add Phone Number"**, click **"Get Started"**
3. Enter phone number details:
   - **Country:** Pakistan (+92)
   - **Phone Number:** Enter a number that can receive SMS/calls
   - **Display Name:** `AI Employee`
   - **Timezone:** (GMT+5:00) Islamabad, Karachi
4. Click **"Verify Code"**
5. Enter the 6-digit code received via SMS/call
6. Click **"Verify"**

#### Option B: Use Existing WhatsApp Business Number

If you already have a WhatsApp Business number:
1. Go to **WhatsApp → Configuration → Phone Numbers**
2. Click **"Add Phone Number"**
3. Select **"Convert Existing Number"**
4. Follow the migration steps

---

### Step 5: Get Your Access Token

1. Go to **WhatsApp → API Setup**
2. Under **"Access Token"** section, you'll see:
   - **Temporary Access Token** (valid for 24 hours - for testing)
   - **Permanent Access Token** (requires business verification)

3. For testing, copy the **Temporary Access Token**
4. Click **"Copy"** button next to the token

> ⚠️ **Important:** Temporary tokens expire in 24 hours. For production, you need business verification.

---

### Step 6: Get Your Business Account ID

1. Go to **WhatsApp → Configuration → Business Account**
2. Copy the **WhatsApp Business Account ID** (WABA ID)
3. This looks like: `123456789012345`

---

### Step 7: Update .env File

Open `.env` file in your project and update:

```env
# WhatsApp Business API Credentials
WHATSAPP_PHONE=123456789012345          # Your Phone Number ID (from Step 4)
WHATSAPP_API_KEY=EAA...xyz              # Your Access Token (from Step 5)
WHATSAPP_BUSINESS_ID=123456789012345    # Your Business Account ID (from Step 6)
```

---

## 🧪 Test Your Setup

Run the API checker:

```bash
py check_whatsapp_api.py
```

**Expected Output:**
```
============================================================
WhatsApp API Message Checker
============================================================

Phone Number ID: 123456789012345
API Key Present: Yes
Business ID: 123456789012345
============================================================

[*] Getting account info...

Account Info: {
  "name": "AI Employee",
  "phone_number": "+923182383594",
  "quality_rating": "GREEN"
}

[OK] Found 1 conversation(s)!
```

---

## 📬 Receiving Messages (Webhook Setup)

To receive messages in real-time:

### Step 8: Configure Webhook

1. Go to **WhatsApp → Configuration → Webhooks**
2. Click **"Edit"** next to Webhook URL
3. Enter your webhook URL:
   ```
   https://your-domain.com/webhook
   ```
4. Click **"Verify and Save"**

### Step 9: Subscribe to Message Events

1. Under **"Webhook Fields"**, select:
   - ✅ `messages`
   - ✅ `message_deliveries`
   - ✅ `message_reads`
2. Click **"Save"**

---

## 🔐 Token Management

### Temporary Token (Testing)
- Valid for: **24 hours**
- Use for: Development and testing
- Refresh: Generate new token from dashboard

### Permanent Token (Production)
- Valid for: **Never expires** (until revoked)
- Requirements:
  - Business verification completed
  - Two-factor authentication enabled
  - Valid business documents

### To Get Permanent Token:

1. Go to **Business Settings** (business.facebook.com)
2. Complete **Business Verification**
3. Add your phone number to Business Manager
4. Generate system user token with `whatsapp_business_messaging` permission

---

## 📊 API Limits

| Limit | Value |
|-------|-------|
| Messages per second | 80 |
| Template messages | Unlimited (pre-approved) |
| Free-form messages | 24-hour window only |
| Media file size | 16 MB max |

---

## 🆘 Troubleshooting

### Error: "Invalid OAuth access token"
- Token expired (generate new one)
- Token copied incorrectly (check for spaces)
- Wrong token type (use WhatsApp token, not Facebook token)

### Error: "Phone number not found"
- Use Phone Number ID, not the actual phone number
- Phone Number ID is numeric (e.g., `123456789012345`)

### Error: "Permission denied"
- App not approved for production
- Missing permissions in App Review
- Token doesn't have required scopes

### Error: "Message template not approved"
- Template messages need Meta approval
- Use free-form messages within 24-hour window
- Submit templates at: WhatsApp → Message Templates

---

## 📚 Useful Links

- **WhatsApp Business API Docs:** https://developers.facebook.com/docs/whatsapp
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer
- **Business Manager:** https://business.facebook.com
- **Meta App Dashboard:** https://developers.facebook.com/apps

---

## ✅ Checklist

- [ ] Created Meta Developer App
- [ ] Added WhatsApp product
- [ ] Added/Verified phone number
- [ ] Copied Phone Number ID
- [ ] Copied Access Token
- [ ] Copied Business Account ID
- [ ] Updated `.env` file
- [ ] Tested with `check_whatsapp_api.py`
- [ ] (Optional) Configured webhook

---

## 🎯 Next Steps

After setup is complete:

1. **Test sending messages:**
   ```python
   from Skills.skill_whatsapp_api import WhatsAppAPISkill
   wa = WhatsAppAPISkill()
   wa.send_message("+923182383594", "Hello from AI Employee!")
   ```

2. **Check for new messages:**
   ```bash
   py check_whatsapp_api.py
   ```

3. **Set up auto-reply watcher:**
   ```bash
   py whatsapp_watcher.py --interval 60
   ```

---

**Need Help?**
- Check error logs in `./Logs/`
- Review API response details
- Visit Meta Developer Support: https://developers.facebook.com/support
