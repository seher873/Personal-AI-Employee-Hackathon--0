# AI Employee Vault 🤖

A multi-phase AI-powered employee automation system for social media management, email processing, and business workflows.

---

## 📋 Project Overview

| Phase | Tier | Status | Approach |
|-------|------|--------|----------|
| Phase 1 | Bronze | ✅ Working | File Watcher |
| Phase 2 | Silver | ✅ Working | Gmail + LinkedIn (Browser) + WhatsApp (Browser) |
| Phase 3 | Gold | ✅ Working | **FB/IG API** + LinkedIn (Browser) + WhatsApp (Browser) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js (for MCP servers)
- Meta Developer Account (for FB/IG APIs)

### Setup

```bash
# Clone and navigate to project
cd AI_Employee_Vault

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r phase3_gold/requirements.txt
```

### Configure Environment

```bash
# Navigate to Phase 3 Gold
cd phase3_gold

# Copy environment template
copy .env.example .env

# Edit .env with your credentials
notepad .env
```

---

## 📁 Project Structure

```
AI_Employee_Vault/
├── Phase1_Bronze/           # Basic file watcher
│   ├── Watchers/
│   │   └── inbox_watcher.py
│   ├── Inbox/
│   ├── Skills/
│   └── Company_Handbook.md
│
├── phase2_silver/           # Email + LinkedIn automation
│   ├── Watchers/
│   │   ├── gmail_watcher.py
│   │   ├── linkedin_watcher.py
│   │   └── whatsapp_*.py
│   ├── email_mcp.py
│   ├── linkedin_auto_post.py
│   └── weekly_audit.py
│
└── phase3_gold/             # API-based social media (Production)
    ├── Skills/
    │   ├── skill_facebook_api.py    ✅ API-based
    │   ├── skill_instagram_api.py   ✅ API-based
    │   ├── skill_whatsapp_api.py    ✅ API-based
    │   └── skill_linkedin_api.py
    ├── Watchers/
    │   ├── watcher_gmail.py
    │   ├── watcher_linkedin.py
    │   └── watcher_whatsapp.py
    ├── social_post_watcher.py       # Main orchestrator
    ├── test_api_credentials.py      # Test setup
    ├── quick_test_post.py           # Quick test
    ├── config.py
    └── .env.example
```

---

## 🎯 Phase 3 Gold - Social Media Automation

### Approach Summary

| Platform | Method | Status |
|----------|--------|--------|
| **Facebook** | ✅ API-Based | Production Ready |
| **Instagram** | ✅ API-Based | Production Ready |
| **LinkedIn** | 🔵 Browser (Playwright) | Working |
| **WhatsApp** | 🔵 Browser (Playwright) | Working |

### Why Mixed Approach?

| Platform | Reason |
|----------|--------|
| **Facebook/Instagram** | API stable, reliable, no browser issues |
| **LinkedIn** | API limited, browser automation more flexible |
| **WhatsApp** | Business API requires approval, browser works immediately |

### Quick Commands

#### Facebook/Instagram (API-Based)

```bash
cd phase3_gold

# Test API credentials
python test_api_credentials.py

# Make a test post
python quick_test_post.py

# Post custom content (Facebook)
python social_post_watcher.py --post "Your message here"

# Post with image (Facebook + Instagram)
python social_post_watcher.py --post "Message" --image "path/to/image.png" --platforms facebook instagram
```

#### LinkedIn (Browser-Based)

```bash
cd phase3_gold

# Post to LinkedIn (browser automation)
python linkedin_auto_post.py

# Or use the skill directly
python Skills/skill_linkedin.py
```

#### WhatsApp (Browser-Based)

```bash
cd phase3_gold

# Monitor WhatsApp messages
python Skills/skill_whatsapp.py

# Or send message
python whatsapp_autoreply.py
```

### Required Credentials

#### For Facebook/Instagram (API)

Add to `phase3_gold/.env`:

```env
# Facebook API
FB_ACCESS_TOKEN=your_access_token
FB_PAGE_ID=your_page_id

# Instagram API
IG_ID=your_instagram_business_id
```

#### For LinkedIn (Browser)

```env
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
```

#### For WhatsApp (Browser)

```env
# No credentials needed - QR code login
```

### Get Your Credentials

1. **Facebook/Instagram API:**
   - Visit: https://developers.facebook.com/tools/explorer/
   - Generate token with: `pages_manage_posts`, `instagram_content_publish`
   - Get Page ID from your Facebook Page
   - Get Instagram Business ID from Meta Business Suite

2. **LinkedIn (Browser):**
   - Use your regular LinkedIn email/password
   - First run will require QR code or 2FA verification

3. **WhatsApp (Browser):**
   - Open WhatsApp Web
   - Scan QR code with your phone
   - Session saved for future use

---

## 📧 Phase 2 Silver - Email + LinkedIn

### Browser-Based Automation

| Platform | Method | Script |
|----------|--------|--------|
| Gmail | OAuth + IMAP | `Watchers/gmail_watcher.py` |
| LinkedIn | Playwright | `linkedin_auto_post.py` |
| WhatsApp | Playwright | `Watchers/whatsapp_*.py` |

```bash
cd phase2_silver

# Test Gmail watcher
python Watchers/gmail_watcher.py

# Test LinkedIn auto-post (browser)
python linkedin_auto_post.py

# Test WhatsApp (browser - QR login)
python Watchers/whatsapp_working.py

# Run weekly audit
python weekly_audit.py
```

---

## 📂 Phase 1 Bronze - File Watcher

```bash
cd Phase1_Bronze

# Run inbox watcher
python Watchers/inbox_watcher.py
```

---

## 🔧 MCP Servers (Optional)

```bash
cd phase3_gold/mcp_servers

# Start Social MCP Server
node mcp_server_social.js

# Start Audit MCP Server
python mcp_server_audit.py

# Test health
curl http://localhost:3000/health
curl http://localhost:3001/health
```

---

## 📊 Logs & Monitoring

All activity is logged to:

| Phase | Log Location |
|-------|--------------|
| Phase 3 Gold | `phase3_gold/Logs/` |
| Phase 2 Silver | `phase2_silver/Logs/` |
| Phase 1 Bronze | `Phase1_Bronze/watcher_output.log` |

---

## ⚠️ Important Notes

### Instagram Images (API)
Instagram API requires **public URLs** for images. Local file paths won't work.

**Solutions:**
1. Upload to cloud storage (Google Drive, Dropbox, S3)
2. Use a public web server
3. Use browser-based skill as fallback

### Facebook Token Expiry (API)
Facebook access tokens expire. If posting fails:
1. Generate new token at Facebook Developer Explorer
2. Update `.env` file
3. Restart your script

### LinkedIn Browser Session
- First run requires login/2FA
- Session saved in `phase3_gold/linkedin_session/`
- Clear session if login issues: delete session folder

### WhatsApp Browser Session
- QR code login required on first run
- Session saved in `phase3_gold/whatsapp_session/`
- Keep phone connected to internet

---

## 📚 Documentation

| Document | Location |
|----------|----------|
| API Setup Guide | `phase3_gold/API_SETUP_COMPLETE.md` |
| API Posting Guide | `phase3_gold/API_POSTING_GUIDE.md` |
| Quick Start API | `phase3_gold/QUICK_START_API.md` |
| WhatsApp Setup | `phase3_gold/WHATSAPP_API_SETUP.md` |
| Complete Setup | `phase3_gold/COMPLETE_SETUP.md` |

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Invalid Access Token | Generate new token at Facebook Developer Explorer |
| Instagram ID not found | Ensure Instagram is Business account connected to FB Page |
| Image URL not accessible | Use public URL for Instagram images |
| Module not found | `pip install -r requirements.txt` |
| Port in use | Change port in config or kill existing process |

---

## 📄 License

MIT License - See LICENSE file for details

---

**Version:** 2.0.0 | **Status:** Production Ready (API-Based) 🚀
