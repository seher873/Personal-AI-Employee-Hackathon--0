# WhatsApp Business API Setup Guide
## AI Employee - Hackathon Edition

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Meta for Developers Account

1. **https://developers.facebook.com/** pe jao
2. Facebook se login karo
3. "My Apps" → "Create App"

---

### Step 2: App Create Karo

1. **App Type:** "Business" select karo
2. **App Name:** `AI Employee WhatsApp`
3. **Contact Email:** apna email daalo
4. **"Create App"** click karo

---

### Step 3: WhatsApp Add Karo

1. Dashboard pe **"WhatsApp"** product dhundo
2. **"Set Up"** click karo
3. WhatsApp Business Account select karo (ya naya banao)

---

### Step 4: Phone Number Add Karo

1. **"Add Phone Number"** click karo
2. Country select karo: **Pakistan (+92)**
3. Phone number daalo: **3001234567** (without +)
4. **SMS verification** code enter karo
5. Done!

---

### Step 5: API Credentials Lo

**WhatsApp Dashboard pe:**
https://developers.facebook.com/apps/YOUR_APP_ID/whatsapp/

#### Temporary Token (Testing ke liye):
- **"API Setup"** section mein dikhega
- **Copy karlo** (24 hours valid)

#### Permanent Token (Production ke liye):

1. **Business Settings** pe jao:
   https://business.facebook.com/settings

2. **Users → System Users**
   - "Add" click karo
   - Name: `AI Employee System`
   - Role: **Admin**
   - Create

3. **Assets Assign Karo:**
   - System User select karo
   - "Add Assets" → "WhatsApp"
   - Apna WhatsApp account select karo
   - **Manage** permission do

4. **Generate Token:**
   - System User → "Generate Access Token"
   - Select WhatsApp account
   - Permissions: `whatsapp_business_messaging`, `whatsapp_business_management`
   - **"Never Expire"** select karo
   - Generate → Copy karlo!

---

### Step 6: `.env` Update Karo

```env
# WhatsApp Business API Credentials
WHATSAPP_PHONE=123456789012345        # Phone Number ID (dashboard se)
WHATSAPP_API_KEY=EAANVcE3rCUYBQ...    # Permanent Access Token
WHATSAPP_BUSINESS_ID=987654321098765  # Business Account ID
```

**Kahan milega:**
- **Phone Number ID:** WhatsApp Dashboard → API Setup → Phone numbers
- **Business Account ID:** Business Settings → Accounts → WhatsApp accounts

---

## 🧪 Test Kaise Karein

### Test Message Bhejo:

```bash
py -c "from social_post_watcher import SocialPostWatcher; w = SocialPostWatcher(); r = w.send_whatsapp_message('+923001234567', 'Hello from AI Employee! 🤖'); print(r)"
```

### Full Demo:

```bash
py hackathon_demo.py "Test message! #AI"
```

---

## 📋 Important Notes

### ✅ Testing Numbers Add Karo:

WhatsApp Business API sirf **verified numbers** pe message bhej sakta hai testing ke liye:

1. **WhatsApp Dashboard → API Setup**
2. **"Manage Phone Number"** → **"To"** section
3. **"Add Recipient Phone Number"**
4. Number daalo with country code: `+923001234567`
5. SMS verification karo

**Sirf inhi numbers pe message jayega!**

---

### ⚠️ Message Templates (Production ke liye):

Agar 24 hours se purana message bhejna ho to **template** banana padta hai:

1. **WhatsApp Manager → Templates**
2. **"Create Template"**
3. Message likho: `Hello {{1}}! This is AI Employee 🤖`
4. Submit for review (24-48 hours)

**Testing ke liye:** Free-form messages kaam karenge verified numbers pe!

---

## 🎯 Hackathon Demo Flow

```bash
# 1. Facebook + Instagram + WhatsApp - All in one!
py hackathon_demo.py "Hackathon Demo! 🚀"

# 2. Sirf WhatsApp
py -c "from social_post_watcher import SocialPostWatcher; w = SocialPostWatcher(); w.send_whatsapp_message('+923001234567', 'Test!')"

# 3. Multiple recipients
py -c "
from social_post_watcher import SocialPostWatcher
w = SocialPostWatcher()
recipients = ['+923001234567', '+923009876543']
for num in recipients:
    w.send_whatsapp_message(num, 'Hello from AI Employee!')
"
```

---

## 🔧 Troubleshooting

### Error: "Phone Number ID not configured"
- `.env` mein `WHATSAPP_PHONE` set karo
- Phone Number ID dashboard se copy karo

### Error: "Invalid access token"
- Token expire ho gaya (24 hours wala tha)
- Permanent token generate karo (Step 5 dekho)

### Error: "Recipient not verified"
- Recipient number ko "To" section mein add karo
- SMS verification complete karo

### Error: "Message template required"
- 24 hours se purana conversation hai
- Testing ke liye naya number use karo (24 hours window)

---

## ✅ Complete Setup Checklist

- [ ] Meta Developer Account bana liya
- [ ] WhatsApp Business App create kar liya
- [ ] Phone number verify kar liya
- [ ] Permanent access token le liya
- [ ] `.env` update kar diya
- [ ] Test numbers add kar diye
- [ ] Test message successfully bhej diya

---

**Ready for Hackathon! 🚀**
