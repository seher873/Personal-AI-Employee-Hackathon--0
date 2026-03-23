# AI Employee Vault 🤖

A multi-phase AI-powered employee automation system for social media management, email processing, and business workflows.

---

## 📋 Project Overview

| Phase | Tier | Status | Approach |
|-------|------|--------|----------|
| Phase 1 | Bronze | ✅ Working | File Watcher |
| Phase 2 | Silver | ✅ Working | Gmail + LinkedIn + WhatsApp |
| Phase 3 | Gold | ✅ Working | **API-Based** (Facebook, Instagram, WhatsApp) |

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

## 🎯 Phase 3 Gold - API-Based Posting (Recommended)

### Why API-Based?

| Feature | Old (Playwright) | New (API) |
|---------|------------------|-----------|
| Reliability | ⚠️ Breaks with UI changes | ✅ Stable |
| Speed | 🐌 Slow (browser) | ⚡ Fast (direct) |
| Login Issues | ❌ Common | ✅ None |
| Session Management | 🔧 Manual | ✅ Automatic |

### Quick Commands

```bash
cd phase3_gold

# 1. Test API credentials
python test_api_credentials.py

# 2. Make a test post
python quick_test_post.py

# 3. Post custom content
python social_post_watcher.py --post "Your message here"

# 4. Post with image (Facebook + Instagram)
python social_post_watcher.py --post "Message" --image "path/to/image.png" --platforms facebook instagram

# 5. Send WhatsApp message
python social_post_watcher.py --post "Message" --whatsapp-to +1234567890

# 6. Run automated watch mode
python social_post_watcher.py --watch --interval 60
```

### Required Credentials

Add to `phase3_gold/.env`:

```env
# Facebook API
FB_ACCESS_TOKEN=your_access_token
FB_PAGE_ID=your_page_id

# Instagram API
IG_ID=your_instagram_business_id

# WhatsApp API (optional)
WHATSAPP_PHONE=your_phone_number_id
WHATSAPP_API_KEY=your_api_key
```

### Get Your Credentials

1. **Facebook/Instagram:**
   - Visit: https://developers.facebook.com/tools/explorer/
   - Generate token with: `pages_manage_posts`, `instagram_content_publish`
   - Get Page ID from your Facebook Page

2. **Instagram Business ID:**
   - Run: `python find_ig_id.py`
   - Or find in Meta Business Suite

3. **WhatsApp Business API:**
   - Set up at: https://developers.facebook.com/docs/whatsapp

---

## 📧 Phase 2 Silver - Email + LinkedIn

```bash
cd phase2_silver

# Test Gmail watcher
python Watchers/gmail_watcher.py

# Test LinkedIn auto-post
python linkedin_auto_post.py

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

### Instagram Images
Instagram API requires **public URLs** for images. Local file paths won't work.

**Solutions:**
1. Upload to cloud storage (Google Drive, Dropbox, S3)
2. Use a public web server
3. Use browser-based skill as fallback

### Token Expiry
Facebook access tokens expire. If posting fails:
1. Generate new token at Facebook Developer Explorer
2. Update `.env` file
3. Restart your script

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
