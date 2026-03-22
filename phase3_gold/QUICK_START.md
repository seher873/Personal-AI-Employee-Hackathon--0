# 🚀 Quick Start: Connect FB + IG + WhatsApp
## 5-Minute Setup Guide

---

## ✅ Step-by-Step (Follow Exactly)

### Step 1: Go to Meta Developers

```
🔗 URL: https://developers.facebook.com/
📧 Login: urojk77@gmail.com
```

---

### Step 2: Create New App

```
1. Click "My Apps" → "Create App"
2. Select: "Business"
3. App Name: "AI Employee Vault"
4. Click "Create App"
```

---

### Step 3: Add 3 Products

**Click "+" on left sidebar and add:**

```
✅ Facebook Login
✅ Instagram Graph API  
✅ WhatsApp
```

---

### Step 4: Get Facebook Token

```
1. Go to: https://developers.facebook.com/tools/explorer/
2. Select app: "AI Employee Vault"
3. Click "Get Token" → "Get User Access Token"
4. Select permissions:
   ☑ pages_manage_posts
   ☑ pages_read_engagement
   ☑ instagram_basic
   ☑ instagram_content_publish
5. Click "Get Access Token" → Login → Approve
6. Copy the token
```

**Get Page Token:**
```
In Graph Explorer, type: GET /me/accounts
Copy the "access_token" value for your page
```

---

### Step 5: Connect Instagram

```
1. Instagram app → Settings → Account
2. "Switch to Professional Account" → Business
3. Connect to your Facebook Page
4. In Graph Explorer: GET /{PAGE_ID}?fields=instagram_business_account
5. Copy the "id" value (Instagram Business ID)
```

---

### Step 6: Setup WhatsApp

```
1. In app dashboard → WhatsApp → Get Started
2. Add Phone Number: +92 328 3490851
3. Verify via SMS code
4. Go to Business Settings → System Users → Add
5. Name: "AI Employee System" → Role: Admin
6. Add Assets → WhatsApp Business Account → Select yours
7. Generate Token → "Never Expires" → Copy token
```

---

### Step 7: Update .env File

```bash
# Open .env file and fill in:

# Facebook
FB_ACCESS_TOKEN=EAAN... (long token from Step 4)
FB_PAGE_ID=946427518563399 (your page ID)

# Instagram  
IG_ID=17841447308298408 (from Step 5)

# WhatsApp
WHATSAPP_PHONE=123456789012345 (Phone Number ID)
WHATSAPP_API_KEY=EAAN... (token from Step 6)
WHATSAPP_BUSINESS_ID=987654321 (Business Account ID)
```

---

### Step 8: Test Connection

```bash
# Run test script
py test_all_platforms.py
```

**Expected Output:**
```
✅ Facebook: CONNECTED
✅ Instagram: CONNECTED
✅ WhatsApp: CONNECTED

🎉 SUCCESS! All platforms are connected!
```

---

## 📞 Your Credentials Summary

| Platform | Credential | Value |
|----------|-----------|-------|
| Facebook | Page ID | `946427518563399` |
| Facebook | Access Token | (get from Step 4) |
| Instagram | Business ID | (get from Step 5) |
| WhatsApp | Phone Number | `+92 328 3490851` |
| WhatsApp | Business ID | (get from Step 6) |

---

## 🎯 What You Can Do Now

```
✅ Post to Facebook via API
✅ Post to Instagram via API
✅ Send WhatsApp messages via API
✅ All 3 platforms connected to ONE app!
```

---

## 📚 Full Documentation

- **Detailed Guide:** `NEW_APP_SETUP_GUIDE.md`
- **Test Scripts:** `test_*.py` files
- **Architecture:** `ARCHITECTURE.md`

---

## ❓ Need Help?

**Common Issues:**

| Problem | Solution |
|---------|----------|
| Token expired | Use Page Access Token (never expires) |
| Instagram not found | Convert to Business account first |
| WhatsApp can't send | Verify phone number with SMS |

**Support Links:**
- Graph API Explorer: https://developers.facebook.com/tools/explorer/
- Business Manager: https://business.facebook.com/settings

---

**Ready? Let's connect all 3 platforms! 🚀**
