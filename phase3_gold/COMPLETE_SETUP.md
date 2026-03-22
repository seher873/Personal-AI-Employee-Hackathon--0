# 🤖 AI Employee - Complete Setup Guide
## Gold Tier - Hackathon Ready

---

## ✅ Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Playwright browser automation
py -m pip install playwright pillow python-dotenv requests

# Install Chromium browser
playwright install chromium
```

### Step 2: Configure `.env`

```bash
# Copy example
copy .env.example .env

# Edit .env with your credentials
```

**Required Credentials:**

```env
# Facebook/Instagram
FB_ACCESS_TOKEN=EAAN...              # Page Access Token (Never Expires)
FB_PAGE_ID=946427518563399           # Your Page ID
IG_ID=17841447308298408              # Instagram Business ID

# WhatsApp (Optional)
WHATSAPP_PHONE=123456789012345       # Phone Number ID
WHATSAPP_API_KEY=EAAN...             # Access Token
WHATSAPP_BUSINESS_ID=987654321       # Business Account ID

# Twitter (Optional)
TWITTER_EMAIL=your@email.com
TWITTER_PASSWORD=yourpassword

# Imgur (For Instagram images)
IMGUR_CLIENT_ID=your_client_id
```

---

## 🚀 Running the System

### Option 1: Quick Test Post

```bash
# Post to Facebook + Instagram
py quick_test_post.py
```

### Option 2: Full Hackathon Demo

```bash
# Post to all platforms with custom message
py hackathon_demo.py "Hello from AI Employee! 🤖 #AI #Hackathon"
```

### Option 3: Start Watchers (Auto-Reply Mode)

```bash
# Terminal 1: Facebook/Instagram Watcher
start py fb_ig_browser_watcher.py

# Terminal 2: WhatsApp Watcher
start py whatsapp_watcher.py

# Terminal 3: Twitter Watcher (optional)
start py twitter_watcher.py

# Terminal 4: Inbox Auto-Reply Processor
start py inbox_auto_reply.py --watch
```

**Windows One-Liner:**
```bash
start py fb_ig_browser_watcher.py && start py whatsapp_watcher.py && start py inbox_auto_reply.py --watch
```

---

## 📁 Project Structure

```
phase3_gold/
├── config.py                    # Configuration loader
├── .env                         # Your credentials (DO NOT COMMIT)
├── .env.example                 # Template
│
├── Skills/                      # Agent Skills
│   ├── skill_facebook_api.py   # Facebook posting
│   ├── skill_instagram_api.py  # Instagram posting (auto Imgur)
│   └── skill_whatsapp_api.py   # WhatsApp messaging
│
├── *_watcher.py                 # Message monitors
│   ├── fb_ig_browser_watcher.py
│   ├── whatsapp_watcher.py
│   └── twitter_watcher.py
│
├── inbox_auto_reply.py          # Auto-reply handler
├── hackathon_demo.py            # Demo script
├── quick_test_post.py           # Quick test
├── social_post_watcher.py       # Unified poster
├── imgur_uploader.py            # Image hosting
│
├── Inbox/                       # New messages (auto-created)
├── Done/                        # Processed messages (auto-created)
├── Logs/                        # Audit logs (auto-created)
└── post_image.png               # Test image
```

---

## 🎯 Features

### ✅ Working Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Facebook Posting** | ✅ | Text + Image posts |
| **Instagram Posting** | ✅ | Auto Imgur upload |
| **WhatsApp Sending** | ✅ | Text messages |
| **FB/IG Monitoring** | ✅ | Browser-based watcher |
| **WhatsApp Monitoring** | ✅ | QR code login |
| **Twitter Monitoring** | ✅ | DMs + Mentions |
| **Auto-Reply** | ✅ | Keyword-based |
| **Audit Logging** | ✅ | Complete trail |
| **Error Recovery** | ✅ | Ralph Wiggum loop |

---

## 🔧 Configuration Details

### Facebook/Instagram Setup

1. **Get Page Access Token:**
   ```
   https://developers.facebook.com/tools/explorer/
   → Get Token → Get User Access Token
   → Permissions: pages_manage_posts, pages_read_engagement
   → Get Page Token from: /me/accounts
   ```

2. **Link Instagram:**
   ```
   Facebook Page → Settings → Instagram → Connect Account
   ```

### WhatsApp Setup

1. **Create WhatsApp Business App:**
   ```
   https://developers.facebook.com/apps
   → Create App → Business → Add WhatsApp
   ```

2. **Verify Phone Number:**
   ```
   WhatsApp Dashboard → Add Phone Number
   → Country: Pakistan (+92)
   → Number: 3283490851
   → SMS Verification
   ```

3. **Get Permanent Token:**
   ```
   Business Settings → System Users → Add
   → Assign WhatsApp Assets
   → Generate Token (Never Expire)
   ```

### Imgur Setup (For Instagram Images)

1. **Register App:**
   ```
   https://api.imgur.com/oauth2/addclient
   → Application name: AI Employee
   → Authorization type: Anonymous
   ```

2. **Copy Client ID to `.env`:**
   ```env
   IMGUR_CLIENT_ID=abc123xyz
   ```

---

## 🧪 Testing

### Test Facebook Post

```bash
py -c "from social_post_watcher import SocialPostWatcher; w = SocialPostWatcher(); w.post_to_facebook('Test!')"
```

### Test Instagram Post

```bash
py -c "from social_post_watcher import SocialPostWatcher; w = SocialPostWatcher(); w.post_to_instagram('Test!', 'https://i.imgur.com/IMAGE.jpg')"
```

### Test WhatsApp Message

```bash
py -c "from social_post_watcher import SocialPostWatcher; w = SocialPostWatcher(); w.send_whatsapp_message('+923283490851', 'Test!')"
```

### Test Auto-Reply

1. Send WhatsApp message to your number
2. Watcher detects it → Saves to Inbox/
3. Auto-reply processor picks it up
4. Sends automatic response

---

## 📊 Monitoring

### Check Logs

```bash
# Today's logs
type Logs\fb_ig_watcher_20260305.log
type Logs\whatsapp_watcher_20260305.log
type Logs\inbox_processor_20260305.log
```

### Check Inbox

```bash
# Unprocessed messages
dir Inbox\

# Processed messages
dir Done\
```

### Audit Trail

```bash
# All actions
type Logs\social_watcher_audit.jsonl
```

---

## 🐛 Troubleshooting

### Playwright Issues

```bash
# Reinstall
py -m pip uninstall playwright
py -m pip install playwright
playwright install chromium
```

### Token Expired

```
Facebook/Instagram tokens expire after 4-6 hours.
Get Page Access Token (Never Expires) from:
https://graph.facebook.com/v18.0/me/accounts?access_token=USER_TOKEN
```

### QR Code Not Scanning (WhatsApp)

```
1. Make sure WhatsApp mobile app is open
2. Go to Settings → Linked Devices
3. Scan QR code on browser
4. Session will persist for future runs
```

### Watcher Not Detecting Messages

```
1. Check if browser is logged in
2. Verify session folder exists
3. Try deleting session folder and re-login
4. Check selectors (platforms update UI frequently)
```

---

## 🎯 Hackathon Demo Flow

### Scenario 1: Social Media Posting

```bash
# CEO sends WhatsApp message
"Post about our new product on Facebook and Instagram!"

# System flow:
1. WhatsApp Watcher detects message
2. Saves to Inbox/20260305_120000_whatsapp_ceo.md
3. Inbox Processor reads message
4. Detects "post" keyword
5. Calls SocialPostWatcher.post_to_all()
6. Posts to Facebook + Instagram
7. Moves file to Done/
```

### Scenario 2: Auto-Reply

```bash
# Customer sends message
"Hi, what are your prices?"

# System flow:
1. Watcher detects message
2. Saves to Inbox
3. Auto-reply detects "prices" keyword
4. Sends: "Pricing info: www.example.com/pricing"
5. Logs to audit trail
```

### Scenario 3: Weekly Audit

```bash
# Every Sunday 9 AM
py weekly_audit.py

# Generates:
- CEO_Briefing.md
- Weekly stats
- Pending tasks summary
```

---

## 📝 Environment Variables Reference

```env
# === Facebook ===
FB_EMAIL=                    # Facebook login email
FB_PASSWORD=                 # Facebook login password
FB_ACCESS_TOKEN=             # Page Access Token (API posting)
FB_PAGE_ID=                  # Facebook Page ID

# === Instagram ===
IG_USERNAME=                 # Instagram login
IG_PASSWORD=                 # Instagram password
IG_ID=                       # Instagram Business ID
IG_ACCESS_TOKEN=             # Page Access Token (same as FB)

# === WhatsApp ===
WHATSAPP_PHONE=              # Phone Number ID
WHATSAPP_API_KEY=            # Access Token
WHATSAPP_BUSINESS_ID=        # Business Account ID

# === Twitter ===
TWITTER_EMAIL=               # Twitter login email
TWITTER_PASSWORD=            # Twitter password

# === Imgur ===
IMGUR_CLIENT_ID=             # Imgur API Client ID

# === MCP Servers ===
MCP_PORT=3000                # Social MCP port
AUDIT_MCP_PORT=3001          # Audit MCP port
```

---

## ✅ Pre-Demo Checklist

- [ ] All credentials in `.env`
- [ ] Facebook Page Access Token (Never Expires)
- [ ] Instagram linked to Facebook Page
- [ ] WhatsApp Business verified
- [ ] Test image exists (`post_image.png`)
- [ ] Playwright installed (`playwright install chromium`)
- [ ] Test post successful
- [ ] Watchers running (if using auto-reply)
- [ ] Logs folder created
- [ ] Inbox/Done folders created

---

## 🏆 Hackathon Submission Ready!

**Gold Tier Requirements:**

| # | Requirement | Status | File |
|---|-------------|--------|------|
| 1 | Silver (all) | ✅ | All working |
| 2 | Cross-domain integration | ✅ | Personal + Business |
| 3 | Odoo (skipped) | ⚠️ | Optional |
| 4 | Facebook + Instagram | ✅ | `skill_facebook_api.py`, `skill_instagram_api.py` |
| 5 | Twitter/X | ✅ | `twitter_watcher.py` |
| 6 | Multiple MCP servers | ✅ | `social_mcp.js`, `audit_mcp.py` |
| 7 | Weekly Audit | ⏳ | `weekly_audit.py` (create if needed) |
| 8 | Error recovery | ✅ | Ralph Wiggum loop |
| 9 | Audit logging | ✅ | `Logs/` folder |
| 10 | Ralph Wiggum loop | ✅ | In orchestrator |
| 11 | Documentation | ✅ | `ARCHITECTURE.md`, `README.md` |
| 12 | Agent Skills | ✅ | `Skills/` folder |

---

**🚀 Ready for Demo!**

```bash
# Final test
py hackathon_demo.py "Hackathon Demo - AI Employee is ready! 🤖"
```

---

**Good Luck! 🎉**
