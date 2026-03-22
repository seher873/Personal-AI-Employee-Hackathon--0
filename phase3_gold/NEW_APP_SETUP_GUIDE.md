# 🆕 New Meta Business App Setup Guide
## Connect Facebook + Instagram + WhatsApp Together

---

## 🎯 Overview

This guide will help you create a **new Meta Business App** that connects all three platforms:

```
┌─────────────────────────────────────────────────────────┐
│              META BUSINESS APP (New)                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Facebook   │  │  Instagram   │  │   WhatsApp   │  │
│  │     Login    │  │  Graph API   │  │    Platform  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │         │
│         └──────────────────┼──────────────────┘         │
│                            │                            │
│                  ┌─────────▼─────────┐                  │
│                  │  Access Tokens    │                  │
│                  │  (Never Expires)  │                  │
│                  └───────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Step 1: Create New Meta Business App

### 1.1 Go to Meta Developers Portal

```
URL: https://developers.facebook.com/
Login with: urojk77@gmail.com
```

### 1.2 Create App

1. Click **"My Apps"** (top right)
2. Click **"Create App"** button
3. Select **"Business"** as app type
4. Fill in details:
   - **App Name:** `AI Employee Vault`
   - **App Contact Email:** `urojk77@gmail.com`
   - **Business Account:** Select your business (or create new)
5. Click **"Create App"**

### 1.3 Add Products

On the left sidebar, click **"+"** to add products:

| # | Product | Purpose | Required? |
|---|---------|---------|-----------|
| 1 | **Facebook Login** | Post to Facebook Pages | ✅ |
| 2 | **Instagram Graph API** | Post to Instagram Business | ✅ |
| 3 | **WhatsApp Business Platform** | Send WhatsApp messages | ✅ |

**Add each product:**
```
Facebook Login → Setup → Web Platform → Save
Instagram Graph API → Setup → Connect Instagram Account
WhatsApp → Setup → Add Phone Number
```

---

## 🔐 Step 2: Get Facebook Page Access Token (Never Expires)

### 2.1 Get User Access Token

1. Go to: **Facebook Graph API Explorer**
   ```
   https://developers.facebook.com/tools/explorer/
   ```

2. Select your app: `AI Employee Vault`

3. Click **"Get Token"** → **"Get User Access Token"**

4. Select permissions:
   - ✅ `pages_manage_posts`
   - ✅ `pages_read_engagement`
   - ✅ `instagram_basic`
   - ✅ `instagram_content_publish`
   - ✅ `whatsapp_business_messaging`
   - ✅ `whatsapp_business_management`

5. Click **"Get Access Token"**
6. Login and approve permissions
7. Copy the **User Access Token**

### 2.2 Get Page Access Token

1. In Graph API Explorer, make this request:
   ```
   GET /me/accounts
   ```

2. Find your page in the response
3. Copy the `access_token` value (this is your **Page Access Token**)

4. **Make it permanent:**
   ```
   GET /oauth/access_token?
     grant_type=fb_exchange_token&
     client_id={APP_ID}&
     client_secret={APP_SECRET}&
     fb_exchange_token={PAGE_ACCESS_TOKEN}
   ```

### 2.3 Save to .env

```env
FB_ACCESS_TOKEN=EAAN... (long token, never expires)
FB_PAGE_ID=946427518563399
FB_APP_ID=your_app_id
FB_APP_SECRET=your_app_secret
```

---

## 📸 Step 3: Connect Instagram Business Account

### 3.1 Requirements

- Instagram account must be **Business** or **Creator** type
- Must be connected to Facebook Page

### 3.2 Convert to Business Account

1. Open Instagram app
2. Go to **Settings** → **Account**
3. Click **"Switch to Professional Account"**
4. Select **"Business"**
5. Connect to your Facebook Page

### 3.3 Get Instagram Business ID

1. Go to Graph API Explorer
2. Make this request:
   ```
   GET /{FB_PAGE_ID}?fields=instagram_business_account
   ```

3. Copy the `id` value (this is your **Instagram Business ID**)

### 3.4 Save to .env

```env
IG_ID=17841447308298408
IG_USERNAME=your_instagram_username
```

---

## 💬 Step 4: Setup WhatsApp Business Platform

### 4.1 Add WhatsApp Product

1. In your app dashboard
2. Click **"WhatsApp"** → **"Get Started"**
3. Click **"Add Phone Number"**

### 4.2 Verify Phone Number

1. Enter phone number: `+92 328 3490851`
2. Select country: **Pakistan**
3. Click **"Send Code"** (via SMS)
4. Enter verification code

### 4.3 Get WhatsApp Business Account ID

1. Go to **WhatsApp → API Setup**
2. Under **"Test"**, you'll see:
   - **Phone Number ID**
   - **WhatsApp Business Account ID**

### 4.4 Get Permanent Access Token

1. Go to **Business Settings**
   ```
   https://business.facebook.com/settings
   ```

2. Navigate to:
   ```
   Users → System Users → Add
   ```

3. Create system user:
   - **Name:** `AI Employee System`
   - **Role:** **Admin**

4. Assign assets:
   - Click **"Add Assets"**
   - Select **WhatsApp Business Account**
   - Select your account
   - Check all permissions

5. Generate token:
   - Click **"Generate New Token"**
   - Select **"Never Expires"**
   - Copy the token

### 4.5 Save to .env

```env
WHATSAPP_PHONE=123456789012345      # Phone Number ID
WHATSAPP_BUSINESS_ID=987654321      # WhatsApp Business Account ID
WHATSAPP_API_KEY=EAAN...            # Permanent Access Token
```

---

## 🧪 Step 5: Test All Connections

### Test Facebook

```bash
py test_facebook_connection.py
```

### Test Instagram

```bash
py test_instagram_connection.py
```

### Test WhatsApp

```bash
py test_whatsapp_connection.py
```

### Test All Together

```bash
py test_all_platforms.py
```

---

## 📊 Step 6: Update Your Code

### config.py (Updated)

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Facebook
FB_ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')
FB_PAGE_ID = os.getenv('FB_PAGE_ID')
FB_APP_ID = os.getenv('FB_APP_ID')
FB_APP_SECRET = os.getenv('FB_APP_SECRET')

# Instagram
IG_ID = os.getenv('IG_ID')
IG_USERNAME = os.getenv('IG_USERNAME')

# WhatsApp
WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE')
WHATSAPP_BUSINESS_ID = os.getenv('WHATSAPP_BUSINESS_ID')
WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY')
```

---

## ✅ Verification Checklist

| Platform | Status | How to Verify |
|----------|--------|---------------|
| Facebook | ⬜ | Can post via API |
| Instagram | ⬜ | Can post via API |
| WhatsApp | ⬜ | Can send messages |
| All Connected | ⬜ | Single app manages all 3 |

---

## 🔧 Troubleshooting

### Token Expires

**Problem:** Access token expires after few hours

**Solution:** Use Page Access Token (never expires)
```
User Token → Page Token → Long-lived Page Token
```

### Instagram Not Connected

**Problem:** Instagram Graph API returns error

**Solution:**
1. Make sure Instagram is Business account
2. Reconnect to Facebook Page
3. Re-approve permissions

### WhatsApp Can't Send

**Problem:** WhatsApp API returns 403

**Solution:**
1. Verify phone number is active
2. Check Business Account ID
3. Regenerate System User token

---

## 📞 Support Links

- **Meta Developers:** https://developers.facebook.com/support/
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
- **Business Manager:** https://business.facebook.com/settings
- **WhatsApp API Docs:** https://developers.facebook.com/docs/whatsapp

---

## 🎯 Next Steps

After setup is complete:

1. ✅ Run `py test_all_platforms.py`
2. ✅ Update `.env` with new tokens
3. ✅ Test posting to all 3 platforms
4. ✅ Start watchers for auto-monitoring

---

**Ready to create your new app! 🚀**
