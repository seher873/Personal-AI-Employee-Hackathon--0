# Gold Tier Skills - AI Employee Vault
## Complete Skill Documentation

**Version:** 1.0.0-Gold (Updated)  
**Generated:** 2026-02-20  
**Tier:** Gold (Production-Ready)

---

## Agent Skills Summary

| Skill | Description | Status |
|-------|-------------|--------|
| 🌐 Cross-Domain Routing | Personal (Gmail/WhatsApp) vs Business (LinkedIn/FB/IG/X) | ✅ Active |
| 🔄 Error Recovery | 3-retry with exponential backoff, graceful skip on fail | ✅ Active |
| 📋 Audit Logging | Every action/error logged to Audit_Log.md with timestamp | ✅ Active |
| 👤 Human-in-the-Loop | Confirmation required for sensitive actions | ✅ Active |
| 🍩 Ralph Wiggum Loop | Strong iterative loop until TASK_COMPLETE | ✅ Active |
| 📊 Weekly Audit | Automated Sunday briefings with CEO_Briefing.md | ✅ Active |
| 🔌 MCP Servers | REST API for social posting & audit generation | ✅ Active |
| 📱 Facebook/Instagram | Playwright browser automation for FB/IG | ✅ Active |
| 🐦 Twitter/X | Playwright browser automation for X | ✅ Active |

---

## Table of Contents

1. [Core Skills Overview](#core-skills-overview)
2. [Cross-Domain Orchestration](#cross-domain-orchestration)
3. [Social Media Platform Skills](#social-media-platform-skills)
4. [Error Recovery System](#error-recovery-system)
5. [Audit & Logging](#audit--logging)
6. [Human-in-the-Loop](#human-in-the-loop)
7. [Ralph Wiggum Loop](#ralph-wiggum-loop)
8. [MCP Server Integration](#mcp-server-integration)
9. [Weekly Audit System](#weekly-audit-system)

---

## Core Skills Overview

| Skill | Description | Status |
|-------|-------------|--------|
| Cross-Domain Routing | Personal (Gmail/WhatsApp) vs Business (LinkedIn/FB/IG/X) | ✅ Active |
| Error Recovery | 3-retry with exponential backoff, graceful skip | ✅ Active |
| Audit Logging | All actions logged to Audit_Log.md with timestamps | ✅ Active |
| Human-in-the-Loop | Confirmation for sensitive actions | ✅ Active |
| Ralph Wiggum Loop | Iterative analysis until TASK_COMPLETE | ✅ Active |
| Weekly Audit | Automated Sunday briefings | ✅ Active |
| MCP Servers | REST API for social posting & audit | ✅ Active |

---

## Cross-Domain Orchestration

### Skill: `ai_orchestrator.py`

**Purpose:** Route messages to correct domain handlers

**Domains:**
```
┌─────────────────────────────────────────────────────┐
│                  AI Orchestrator                     │
├─────────────────────────────────────────────────────┤
│  📱 PERSONAL DOMAIN        │  💼 BUSINESS DOMAIN    │
│  ├─ Gmail                  │  ├─ LinkedIn           │
│  └─ WhatsApp               │  ├─ Facebook           │
│                            │  ├─ Instagram          │
│                            │  └─ X (Twitter)        │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Message classification by source/keywords
- Subprocess routing to watcher/poster scripts
- Ralph Wiggum loop for each task
- 3-retry error recovery per message

**Usage:**
```bash
python ai_orchestrator.py
```

---

## Social Media Platform Skills

### 1. Facebook/Instagram (`fb_ig_browser_poster.py`, `fb_ig_browser_watcher.py`)

**Agent Skills:**
- Persistent browser sessions (`./fb_ig_session`)
- Human-like typing & mouse movements
- Image upload support
- 60s polling for messages/comments
- Screenshot audit trail

**Credentials:**
```bash
FB_EMAIL=your@email.com
FB_PASSWORD=your_password
IG_USERNAME=your_username
IG_PASSWORD=your_password
```

**Usage:**
```bash
# Post to both platforms
python fb_ig_browser_poster.py --text "Hello" --image /path/to/img.jpg

# Watch for messages
python fb_ig_browser_watcher.py --interval 60
```

### 2. Twitter/X (`twitter_browser_poster.py`, `twitter_browser_watcher.py`)

**Agent Skills:**
- Persistent browser sessions (`./twitter_session`)
- Multi-step login handling
- Tweet composition with media
- Mention/reply monitoring
- Ralph Wiggum retry loop

**Credentials:**
```bash
TWITTER_EMAIL=your@email.com
TWITTER_PASSWORD=your_password
```

**Usage:**
```bash
# Post tweet
python twitter_browser_poster.py --text "Hello World"

# Watch mentions
python twitter_browser_watcher.py --interval 60
```

---

## Error Recovery System

### Skill: Universal Error Handling

**Implementation:** All scripts

**Features:**
- **3 Retry Attempts** with exponential backoff (2s, 4s, 8s)
- **Graceful Skip** on final failure
- **Error Logging** to Audit_Log.md
- **Continued Processing** (one failure doesn't stop pipeline)

**Pattern:**
```python
MAX_RETRIES = 3
RETRY_DELAY = 2

def run_with_retry(func, *args):
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                log_error(f"Failed after {MAX_RETRIES} attempts: {e}")
                return None  # Graceful skip
            time.sleep(RETRY_DELAY * (2 ** attempt))
```

---

## Audit & Logging

### Skill: Comprehensive Audit Trail

**Log File:** `Audit_Log.md`

**Format:**
```markdown
### [2026-02-20T22:01:30] TASK: task_001

- **Action**: PROCESS
- **Domain**: business
- **Status**: SUCCESS
- **Details**: Script: linkedin_watcher.py, Retries: 0

---
```

**Logged Events:**
- ✅ Task start/completion
- ⚠️ Errors and retries
- 🔄 Ralph Wiggum iterations
- 📊 Weekly audit summaries
- 👤 Human-in-the-loop decisions

**Usage in Scripts:**
```python
from audit_logger import AuditLogger

audit = AuditLogger("Audit_Log.md")
audit.log_task("task_001", "PROCESS", "business", "SUCCESS")
```

---

## Human-in-the-Loop

### Skill: Sensitive Action Confirmation

**Triggers:**
- First-time login to new platform
- Large batch operations (>10 items)
- Financial/revenue-related actions
- Account security changes

**Implementation:**
```python
def confirm_sensitive_action(action: str) -> bool:
    """Require human confirmation for sensitive actions"""
    print(f"⚠️  SENSITIVE ACTION: {action}")
    response = input("Confirm? (yes/no): ")
    return response.lower() == 'yes'
```

**Environment Override:**
```bash
# Skip confirmations for automated runs
export AUTO_CONFIRM=true
```

---

## Ralph Wiggum Loop

### Skill: Iterative Task Completion

**Quote:** *"Me fail English? That's unpossible!"*

**Implementation:**
```python
class RalphWiggumLoop:
    def __init__(self, max_iterations=10):
        self.max_iterations = max_iterations
        self.current_iteration = 0
    
    def next_iteration(self) -> bool:
        self.current_iteration += 1
        if self.current_iteration > self.max_iterations:
            self.fail()
            return False
        return True
    
    def complete(self):
        self.status = "TASK_COMPLETE"
        logger.info("🍩 Ralph Wiggum Loop: 'I did it!'")
```

**Usage:**
- Task processing until success
- Data analysis iterations
- Retry failed operations
- Content generation refinement

---

## MCP Server Integration

### 1. Social Media MCP (`social_mcp.js`)

**Port:** 3000

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/post-fb` | POST | Post to Facebook |
| `/post-ig` | POST | Post to Instagram |
| `/post-x` | POST | Post to Twitter/X |
| `/post-all` | POST | Post to all platforms |
| `/health` | GET | Health check |

**Usage:**
```bash
curl -X POST http://localhost:3000/post-x \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World"}'
```

### 2. Audit MCP (`audit_mcp.py`)

**Port:** 3001

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate_briefing` | POST | Generate CEO_Briefing.md |
| `/briefing` | GET | Get current briefing |
| `/vault-summary` | GET | Summary of vault contents |
| `/audit` | POST | Run audit |
| `/health` | GET | Health check |

**Usage:**
```bash
curl -X POST http://localhost:3001/generate_briefing
```

---

## Weekly Audit System

### Skill: `weekly_audit.py`

**Schedule:** Every Sunday at 9:00 AM

**Cron Setup:**
```bash
# Edit crontab
crontab -e

# Add line:
0 9 * * 0 cd /path/to/phase3_gold && source .venv/bin/activate && python weekly_audit.py >> Logs/weekly_audit.log 2>&1
```

**Process:**
1. 📂 Read vault (Inbox/Needs_Action/Done)
2. 🍩 Ralph Wiggum analysis loop
3. 📊 Categorize (revenue/bottlenecks/tasks)
4. 📄 Generate CEO_Briefing.md
5. 📡 Call audit_mcp endpoints
6. 📝 Log to Audit_Log.md

**Output:**
- `CEO_Briefing.md` - Executive summary
- `Audit_Log.md` - Audit trail entry

**Usage:**
```bash
# Force run (any day)
python weekly_audit.py --force

# Normal run (Sundays only)
python weekly_audit.py
```

---

## File Structure

```
phase3_gold/
├── ai_orchestrator.py          # Main orchestrator
├── weekly_audit.py             # Weekly audit script
├── fb_ig_browser_poster.py     # FB/IG posting
├── fb_ig_browser_watcher.py    # FB/IG monitoring
├── twitter_browser_poster.py   # Twitter posting
├── twitter_browser_watcher.py  # Twitter monitoring
├── social_mcp.js               # Social media MCP server
├── audit_mcp.py                # Audit MCP server
├── Audit_Log.md                # Audit trail
├── CEO_Briefing.md             # Executive briefings
├── Inbox/                      # Incoming messages
├── Needs_Action/               # Pending items
├── Done/                       # Completed tasks
├── Logs/                       # Application logs
├── Screenshots/                # Visual audit trail
├── fb_ig_session/              # FB/IG browser sessions
├── twitter_session/            # Twitter browser sessions
└── .env                        # Credentials (gitignored)
```

---

## Environment Variables

```bash
# Facebook
FB_EMAIL=your_facebook_email
FB_PASSWORD=your_facebook_password

# Instagram
IG_USERNAME=your_instagram_username
IG_PASSWORD=your_instagram_password

# Twitter/X
TWITTER_EMAIL=your_twitter_email
TWITTER_PASSWORD=your_twitter_password

# MCP Servers
MCP_PORT=3000
AUDIT_MCP_PORT=3001
AUDIT_MCP_URL=http://localhost:3001

# Automation
AUTO_CONFIRM=false  # Set true to skip human confirmations
```

---

## Quick Start

```bash
# 1. Setup virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install playwright python-dotenv
playwright install chromium
npm install

# 3. Configure credentials
cp .env.example .env
# Edit .env with your credentials

# 4. Start MCP servers (in separate terminals)
node social_mcp.js &
python audit_mcp.py &

# 5. Run orchestrator
python ai_orchestrator.py

# 6. Generate weekly briefing
python weekly_audit.py --force
```

---

## Health Checks

```bash
# Check Social MCP
curl http://localhost:3000/health

# Check Audit MCP
curl http://localhost:3001/health

# View current briefing
curl http://localhost:3001/briefing
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login fails | Check credentials in .env, verify 2FA is disabled |
| MCP not responding | Start servers: `node social_mcp.js`, `python audit_mcp.py` |
| Playwright errors | Run `playwright install chromium` |
| Permission denied | Run `chmod +x *.py *.js` |

---

## Gold Tier Capabilities Summary

| Capability | Silver Tier | Gold Tier |
|------------|-------------|-----------|
| Platforms | LinkedIn, WhatsApp | + Facebook, Instagram, Twitter/X |
| Error Recovery | Basic | 3-retry + exponential backoff |
| Logging | Console | Audit_Log.md + timestamps |
| Human-in-the-Loop | None | Sensitive action confirmation |
| Ralph Wiggum Loop | Basic | Full iteration with status |
| Weekly Audit | Manual | Automated cron + briefing |
| MCP Servers | None | Social + Audit REST APIs |
| Cross-Domain | No | Personal vs Business routing |

---

*Generated by Gold Tier AI Employee Vault*  
*Agent Skill: Documentation*
