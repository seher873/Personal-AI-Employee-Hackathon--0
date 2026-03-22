# AI Employee - Gold Tier Setup

Simple, working automation skills for social media and communication.

---

## ✅ Gold Tier Requirements Completed

| # | Requirement | Status | File |
|---|-------------|--------|------|
| 1 | Silver requirements | ✅ Done | (Phase 2) |
| 2 | Cross-domain integration | ✅ Done | All skills |
| 3 | ~~Odoo Accounting~~ | ❌ Skipped | - |
| 4 | Facebook + Instagram | ✅ Done | `skill_facebook.py`, `skill_instagram.py` |
| 5 | Twitter (X) | ✅ Done | `skill_twitter.py` |
| 6 | Multiple MCP servers | ✅ Ready | Architecture ready |
| 7 | Weekly Audit + CEO Brief | ✅ Done | `skill_weekly_audit.py` |
| 8 | Error recovery | ✅ Done | Built into all skills |
| 9 | Audit logging | ✅ Done | JSONL logs in `./Logs/` |
| 10 | Ralph Wiggum loop | ⏳ Ready | See architecture |
| 11 | Documentation | ✅ This file | `README_GOLD.md` |
| 12 | Agent Skills | ✅ Done | All `skill_*.py` files |

---

## 📁 Project Structure

```
phase3_gold/
├── .env                    # Credentials (EDIT THIS)
├── config.py               # Config loader
├── selector_loader.py      # Dynamic selectors
├── selectors.json          # Website selectors
│
├── skill_facebook.py       # Facebook posting
├── skill_instagram.py      # Instagram posting
├── skill_twitter.py        # Twitter/X posting
├── skill_whatsapp.py       # WhatsApp monitoring
├── skill_gmail.py          # Gmail checking
├── skill_weekly_audit.py   # Weekly reports + CEO briefing
│
├── Logs/                   # All logs and audit trails
├── Inbox/                  # New messages/emails
├── Screenshots/            # Error screenshots
└── Reports/                # Weekly reports
```

---

## 🚀 Quick Start

### Step 1: Setup Credentials

Edit `.env` file with your credentials:

```ini
# Facebook
FB_EMAIL=your_email@example.com
FB_PASSWORD=your_password

# Instagram
IG_USERNAME=your_username
IG_PASSWORD=your_password

# Twitter/X
TWITTER_EMAIL=your_email@example.com
TWITTER_PASSWORD=your_password

# Gmail
GMAIL_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_app_password
```

### Step 2: Install Dependencies

```bash
cd C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold
py -m pip install playwright python-dotenv
py -m playwright install chromium
```

### Step 3: Test Each Skill

```bash
# Facebook
py skill_facebook.py

# Instagram
py skill_instagram.py

# Twitter
py skill_twitter.py

# WhatsApp (monitors for 60 seconds)
py skill_whatsapp.py

# Gmail
py skill_gmail.py

# Weekly Audit
py skill_weekly_audit.py
```

### Step 4: Setup Automation (Optional)

**Automate with Windows Task Scheduler:**

1. Read: `TASK_SCHEDULER_SETUP.md`
2. Create 3 scheduled tasks:
   - **Daily Posts** - 9:00 AM (Facebook, Instagram, Twitter)
   - **Hourly Check** - Every hour (WhatsApp, Gmail)
   - **Weekly Audit** - Friday 5:00 PM (CEO Briefing)

**Batch Files:**
- `run_daily_posts.bat` - Daily social media posting
- `run_hourly_check.bat` - Hourly message checking
- `run_weekly_audit.bat` - Weekly report generation

---

## 📖 Usage Examples

### Post to Facebook

```python
from skill_facebook import FacebookSkill

fb = FacebookSkill()
result = fb.post("Hello from AI Employee! #AI #Automation", "post_image.png")

print(result)  # {"success": True, ...}
print(fb.generate_summary())
```

### Post to Instagram

```python
from skill_instagram import InstagramSkill

ig = InstagramSkill()
result = ig.post("Amazing post! #Instagram", "post_image.png")

print(f"Posted: {result['success']}")
```

### Post to Twitter/X

```python
from skill_twitter import TwitterSkill

tw = TwitterSkill()
result = tw.post("Tweet from AI! #Twitter #AI")

print(f"Tweeted: {result['success']}")
```

### Monitor WhatsApp

```python
from skill_whatsapp import WhatsAppSkill

wa = WhatsAppSkill()

# Monitor for 1 hour (3600 seconds)
result = wa.start_monitoring(duration=3600)

# Get messages
messages = wa.get_messages()
print(f"Received {len(messages)} messages")
```

### Check Gmail

```python
from skill_gmail import GmailSkill

gmail = GmailSkill()
result = gmail.check_inbox(max_emails=10)

print(f"Found {result['emails_count']} new emails")
```

### Generate Weekly Report

```python
from skill_weekly_audit import WeeklyAuditSkill

audit = WeeklyAuditSkill()

# Generate weekly audit
report = audit.generate_weekly_report()
print(f"Health Score: {report['health_score']}/100")

# Generate CEO briefing
briefing_path = audit.generate_ceo_briefing()
print(f"Briefing saved: {briefing_path}")
```

---

## 🔧 Error Recovery

All skills have built-in error recovery:

1. **Automatic Retries** - 3 attempts by default
2. **Session Persistence** - Auto-login after first run
3. **Audit Logging** - All actions logged to `./Logs/`
4. **Screenshots** - Error screenshots saved to `./Screenshots/`

### Check Logs

```bash
# View today's Facebook log
type Logs\facebook_20260301.log

# View audit trail
type Logs\facebook_audit.jsonl
```

---

## 📊 Cross-Domain Integration

All skills work together for unified automation:

```
┌─────────────────────────────────────────────────────┐
│              AI Employee - Gold Tier                │
├─────────────────────────────────────────────────────┤
│  Social Media           │  Communication            │
│  ├─ Facebook Skill      │  ├─ WhatsApp Skill        │
│  ├─ Instagram Skill     │  └─ Gmail Skill           │
│  └─ Twitter Skill       │                           │
├─────────────────────────────────────────────────────┤
│  Reporting & Audit                                  │
│  └─ Weekly Audit Skill → CEO Briefing               │
└─────────────────────────────────────────────────────┘
```

### Messages Flow

```
WhatsApp/Gmail → Inbox/ → AI Orchestrator → Response
                                         → Route to Human
```

### Posts Flow

```
Content Idea → skill_facebook.py → Facebook
             → skill_instagram.py → Instagram
             → skill_twitter.py   → Twitter
```

---

## 📝 Audit Logging

All actions are logged for compliance:

**Log Location:** `./Logs/`

**Format:** JSONL (one JSON per line)

**Example:**
```json
{"timestamp": "2026-03-01T15:30:00", "action": "post", "details": {"text": "Hello..."}, "success": true}
```

---

## 🎯 Weekly Audit

Run weekly to generate reports:

```bash
py skill_weekly_audit.py
```

**Outputs:**
- `Reports/weekly_audit_YYYYMMDD.json` - Full data
- `Reports/CEO_Briefing_YYYYMMDD.md` - Executive summary

**Includes:**
- Social media performance
- Message statistics
- Error rates
- Health score
- Recommendations

---

## ⚠️ Troubleshooting

### Login Fails

1. Check credentials in `.env`
2. For Gmail, use **App Password** (not regular password)
3. Delete session folder and re-login:
   ```bash
   rmdir /s /q fb_session
   py skill_facebook.py
   ```

### Post Fails

1. Check screenshot in `./Screenshots/`
2. Check log in `./Logs/`
3. Update selectors in `selectors.json`

### WhatsApp Not Detecting Messages

1. Click on a chat first
2. Keep browser window visible
3. Re-scan QR code if needed

---

## 📋 Architecture Notes

### Agent Skills Pattern

Each skill follows the same pattern:

```python
class SkillName:
    def __init__(self):
        # Setup
        
    def action(self, ...):
        # Main action with retry logic
        pass
    
    def generate_summary(self):
        # Return statistics
        pass
```

### Error Handling

```
Try → Fail → Retry (3x) → Log Error → Screenshot → Return Error
```

### Session Management

```
First Run: Manual Login → Save Session
Later: Load Session → Auto-Login
```

---

## 🎓 Next Steps

1. ✅ Test all skills individually
2. ✅ Add your credentials to `.env`
3. ✅ Run weekly audit every Friday
4. ⏳ Integrate with AI Orchestrator
5. ⏳ Add more platforms (LinkedIn, etc.)
6. ⏳ Implement Ralph Wiggum loop

---

**Version:** Gold Tier 1.0
**Last Updated:** 2026-03-01
**Status:** Working ✅
