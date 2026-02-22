# Personal AI Employee Hackathon - Architecture
## Silver + Gold Tier (Odoo Skipped)

> **Tagline:** Your Autonomous Digital FTE — Working 168 Hours/Week While Humans Work 40

**Version:** 1.0.0  
**Date:** 2026-02-21  
**Tier:** Gold (Production-Ready)

---

## Table of Contents

1. [Introduction](#introduction)
2. [High-Level Architecture](#high-level-architecture)
3. [Components](#components)
4. [How It Works: Message Flow](#how-it-works-message-flow)
5. [Lessons Learned](#lessons-learned)
6. [Conclusion: The Digital FTE](#conclusion-the-digital-fte)

---

## Introduction

### Purpose

This system is a **Personal AI Employee** — an autonomous agent that acts as a full-time digital worker, monitoring communication channels, processing messages, executing tasks, and maintaining a persistent memory system. Unlike traditional automation, this is designed as a true **FTE (Full-Time Employee)** replacement that works continuously across personal and business domains.

### What Makes This Different

| Traditional Automation | AI Employee (This System) |
|------------------------|---------------------------|
| Single-purpose scripts | Multi-domain orchestration |
| No memory | Obsidian vault persistence |
| No reasoning | Ralph Wiggum iterative loop |
| No human-in-the-loop | Approval gates for sensitive actions |
| No audit trail | Comprehensive logging |
| 9-5 operation | 24/7/365 operation (168 hrs/week) |

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PERSONAL AI EMPLOYEE SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         🧠 BRAIN LAYER                                │   │
│  │  ┌─────────────────┐    ┌─────────────────────────────────────────┐  │   │
│  │  │  Claude Code    │    │  Ralph Wiggum Loop                      │  │   │
│  │  │  (Reasoning)    │◄──►│  (Iterative Task Completion)            │  │   │
│  │  └─────────────────┘    └─────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    ▲                                         │
│                                    │                                         │
│  ┌─────────────────────────────────┼──────────────────────────────────────┐   │
│  │                         🎯 ORCHESTRATOR                                │   │
│  │                         ai_orchestrator.py                             │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  Cross-Domain Router: Personal vs Business Classification       │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         │                          │                          │             │
│         ▼                          ▼                          ▼             │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐       │
│  │ 👁️ WATCHERS  │           │ 🤖 HANDS    │           │ 💾 MEMORY   │       │
│  │ (Input)     │           │ (Output)    │           │ (Storage)   │       │
│  │             │           │             │           │             │       │
│  │ ┌─────────┐ │           │ ┌─────────┐ │           │ ┌─────────┐ │       │
│  │ │ Gmail   │ │           │ │ Email   │ │           │ │ Inbox/  │ │       │
│  │ │ Watcher │ │           │ │ MCP     │ │           │ │ Needs_  │ │       │
│  │ └─────────┘ │           │ └─────────┘ │           │ │ Action/ │ │       │
│  │ ┌─────────┐ │           │ ┌─────────┐ │           │ │ Done/   │ │       │
│  │ │ WhatsApp│ │           │ │ Social  │ │           │ │ SKILL.md│ │       │
│  │ │ Watcher │ │           │ │ MCP     │ │           │ └─────────┘ │       │
│  │ └─────────┘ │           │ └─────────┘ │           │ ┌─────────┐ │       │
│  │ ┌─────────┐ │           │ ┌─────────┐ │           │ │ Audit_  │ │       │
│  │ │ LinkedIn│ │           │ │ Audit   │ │           │ │ Log.md  │ │       │
│  │ │ Watcher │ │           │ │ MCP     │ │           │ └─────────┘ │       │
│  │ └─────────┘ │           │ └─────────┘ │           └─────────────┘       │
│  │ ┌─────────┐ │           └─────────────┘                                 │
│  │ │ FB/IG   │ │                                                          │
│  │ │ Watcher │ │           ┌─────────────┐                                │
│  │ └─────────┘ │           │ 👤 HUMAN    │                                │
│  │ ┌─────────┐ │           │ IN THE LOOP │                                │
│  │ │ Twitter │ │           │ (Approval)  │                                │
│  │ │ Watcher │ │           └─────────────┘                                │
│  │ └─────────┘ │                                                          │
│  └─────────────┘                                                          │
│                                    │                                         │
│  ┌─────────────────────────────────┼──────────────────────────────────────┐   │
│  │                         ⏰ SCHEDULING (cron)                           │   │
│  │  • Watchers: Continuous polling (60s intervals)                        │   │
│  │  • Weekly Audit: Sundays 9:00 AM                                       │   │
│  │  • Orchestrator: On-demand / triggered                                 │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Summary

```
External Channels → Watchers → Orchestrator → Brain → MCP Hands → External Actions
                              ↓                    ↓
                        Memory (Obsidian)    Human Approval
```

---

## Components

### 🧠 Brain: Claude Code + Ralph Wiggum Loop

#### Claude Code
The reasoning engine that processes messages, makes decisions, and generates responses.

**Role:**
- Natural language understanding
- Task classification
- Response generation
- Decision making

#### Ralph Wiggum Loop
Named after the Simpsons character: *"Me fail English? That's unpossible!"*

**Purpose:** Iterative task completion with retry logic

```python
class RalphWiggumLoop:
    def __init__(self, max_iterations=10):
        self.max_iterations = max_iterations
        self.current_iteration = 0

    def next_iteration(self) -> bool:
        """Continue if under max iterations"""
        self.current_iteration += 1
        if self.current_iteration > self.max_iterations:
            self.fail()
            return False
        return True

    def complete(self):
        """Mark task as TASK_COMPLETE"""
        self.status = "TASK_COMPLETE"
```

**Why It Works:**
- Handles transient failures gracefully
- Allows multi-step task completion
- Provides clear success/failure states

---

### 💾 Memory: Obsidian Vault

The persistent memory system using a simple folder structure.

```
AI_Employee_Vault/
├── Inbox/              # New incoming messages (unprocessed)
├── Needs_Action/       # Tasks requiring attention
├── Done/               # Completed tasks (audit trail)
├── SKILL.md            # Agent capabilities documentation
├── Dashboard.md        # Real-time status overview
├── CEO_Briefing.md     # Weekly executive summaries
└── Audit_Log.md        # Complete action history
```

**File Naming Convention:**
- `YYYYMMDD_HHMMSS_source_description.md`

**Example Inbox Entry:**
```markdown
---
created: 2026-02-21T10:30:00
source: whatsapp
status: pending
---

# Message from +1234567890

"Can you post about our new product on LinkedIn?"

## Action Required
- Classify: Business domain
- Route: LinkedIn poster
- Approval: Required (first post)
```

---

### 👁️ Watchers: Playwright-Based Monitoring

All watchers use **Playwright** browser automation for reliable, human-like interaction.

| Platform | Script | Interval | Session Storage |
|----------|--------|----------|-----------------|
| Gmail | `gmail_watcher.py` | 60s | Cookies |
| WhatsApp | `whatsapp_watcher.py` | 60s | `./whatsapp_session/` |
| LinkedIn | `linkedin_watcher.py` | 60s | `./linkedin_session/` |
| Facebook/Instagram | `fb_ig_browser_watcher.py` | 60s | `./fb_ig_session/` |
| Twitter/X | `twitter_browser_watcher.py` | 60s | `./twitter_session/` |

**Watcher Pattern:**
```python
def watch_with_retry():
    """Standard watcher with error recovery"""
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            # 1. Launch browser with persistent context
            # 2. Navigate to platform
            # 3. Check for new messages/notifications
            # 4. Save to Inbox if found
            # 5. Screenshot for audit
            return success
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                log_error(f"Watcher failed: {e}")
                return None  # Graceful skip
            time.sleep(2 ** attempt)  # Exponential backoff
```

**Key Features:**
- Persistent sessions (no repeated logins)
- Human-like delays and mouse movements
- Screenshot audit trail
- Graceful error handling

---

### 🎯 Orchestrator: Routing & Reasoning

**File:** `ai_orchestrator.py`

**Responsibilities:**
1. **Classification:** Personal vs Business domain
2. **Routing:** Select appropriate watcher/handler
3. **Reasoning:** Invoke Claude Code for complex decisions
4. **MCP Calls:** Trigger appropriate MCP server endpoints
5. **Logging:** Record all actions to Audit_Log.md

**Domain Classification:**
```
PERSONAL DOMAIN          BUSINESS DOMAIN
├── Gmail                ├── LinkedIn
└── WhatsApp             ├── Facebook
                         ├── Instagram
                         └── Twitter/X
```

**Orchestration Flow:**
```python
def orchestrate(message):
    domain = classify_domain(message)  # personal or business
    
    if domain == "personal":
        route_to_personal_handler(message)
    else:
        route_to_business_handler(message)
    
    # Ralph Wiggum loop for retry
    loop = RalphWiggumLoop()
    while not task_complete and loop.next_iteration():
        result = execute_task(message)
        if result:
            loop.complete()
```

---

### 🤖 Hands: MCP Servers

Multiple MCP (Model Context Protocol) servers expose capabilities as REST APIs.

#### 1. Social Media MCP (`social_mcp.js`)

**Port:** 3000

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/post-fb` | POST | Post to Facebook |
| `/post-ig` | POST | Post to Instagram |
| `/post-x` | POST | Post to Twitter/X |
| `/post-all` | POST | Broadcast to all platforms |
| `/health` | GET | Health check |

**Usage:**
```bash
curl -X POST http://localhost:3000/post-x \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "image": "/path/to/img.jpg"}'
```

#### 2. Audit MCP (`audit_mcp.py`)

**Port:** 3001

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate_briefing` | POST | Generate CEO_Briefing.md |
| `/briefing` | GET | Get current briefing |
| `/vault-summary` | GET | Summary of vault contents |
| `/audit` | POST | Run full audit |
| `/health` | GET | Health check |

**Usage:**
```bash
curl -X POST http://localhost:3001/generate_briefing
curl http://localhost:3001/briefing
```

---

### 👤 Human-in-the-Loop Approval

**Purpose:** Prevent unauthorized sensitive actions

**Triggers:**
- First-time login to any platform
- Batch operations (>10 items)
- Financial/revenue-related actions
- Account security changes
- New contact interactions

**Implementation:**
```python
def confirm_sensitive_action(action: str) -> bool:
    """Require human confirmation"""
    print(f"⚠️  SENSITIVE ACTION: {action}")
    
    # Check environment override
    if os.getenv("AUTO_CONFIRM") == "true":
        return True
    
    response = input("Confirm? (yes/no): ")
    return response.lower() == 'yes'
```

**Environment Override:**
```bash
export AUTO_CONFIRM=true  # Skip for automated runs
```

---

### ⏰ Scheduling (cron)

**System:** Unix cron + Python scheduling

| Task | Schedule | Command |
|------|----------|---------|
| Watchers | Continuous | `python *_watcher.py --interval 60` |
| Weekly Audit | Sundays 9:00 AM | `python weekly_audit.py` |
| Orchestrator | On-demand | `python ai_orchestrator.py` |

**Cron Setup:**
```bash
# Edit crontab
crontab -e

# Add weekly audit (Sundays at 9 AM)
0 9 * * 0 cd /path/to/phase3_gold && source .venv/bin/activate && python weekly_audit.py >> Logs/weekly_audit.log 2>&1

# Add watcher (every minute)
* * * * * cd /path/to/phase3_gold && source .venv/bin/activate && python twitter_browser_watcher.py >> Logs/twitter_watcher.log 2>&1
```

**Weekly Audit Process:**
1. Read all vault folders (Inbox, Needs_Action, Done)
2. Ralph Wiggum analysis loop
3. Categorize by type (revenue, bottlenecks, tasks)
4. Generate `CEO_Briefing.md`
5. Call audit_mcp endpoints
6. Log to Audit_Log.md

---

## How It Works: Message Flow

### Example: WhatsApp Message → Task → Social Post

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: MESSAGE ARRIVES                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WhatsApp Message from CEO:                                                 │
│  "Hey, can you post our product launch announcement on LinkedIn?"           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: WHATSAPP WATCHER PICKS UP MESSAGE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Launch browser with persistent session                                  │
│  2. Navigate to WhatsApp Web                                                │
│  3. Detect new message from CEO                                             │
│  4. Save to Inbox/20260221_103000_whatsapp_ceo_request.md                   │
│  5. Take screenshot for audit                                               │
│  6. Log to Audit_Log.md                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: ORCHESTRATOR PROCESSES INBOX                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Read new file from Inbox                                                │
│  2. Classify domain: BUSINESS (LinkedIn = professional network)             │
│  3. Extract intent: SOCIAL_POST                                           │
│  4. Check human-in-loop: First post? → Require approval                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: BRAIN (CLAUDE) REASONS                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Claude analyzes:                                                           │
│  - Intent: Post product launch announcement                                 │
│  - Platform: LinkedIn (business domain)                                     │
│  - Content: Needs draft generation                                          │
│  - Approval: Required (sensitive action)                                    │
│                                                                             │
│  Output: Draft post + approval request                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: HUMAN APPROVAL                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  System: ⚠️  SENSITIVE ACTION: Post to LinkedIn                             │
│  Draft: "Excited to announce our new product! [details]"                    │
│  Confirm? (yes/no): yes                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: MCP HAND EXECUTES                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Orchestrator calls social_mcp.js                                        │
│  2. POST http://localhost:3000/post-linkedin                                │
│  3. MCP launches browser with LinkedIn session                              │
│  4. Composes post with draft text                                           │
│  5. Submits post                                                            │
│  6. Takes confirmation screenshot                                           │
│  7. Returns success response                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 7: MEMORY UPDATE                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Move file: Inbox → Done/                                                │
│  2. Update status: pending → completed                                      │
│  3. Log to Audit_Log.md:                                                    │
│     ### [2026-02-21T10:35:00] TASK: whatsapp_ceo_request                    │
│     - Action: SOCIAL_POST                                                   │
│     - Domain: business                                                      │
│     - Status: SUCCESS                                                       │
│     - Details: Posted to LinkedIn                                           │
│  4. Update Dashboard.md: Active Tasks → Completed Tasks                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 8: RALPH WIGGUM LOOP COMPLETE                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🍩 "I did it!" — TASK_COMPLETE                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Lessons Learned

### What Worked Well

#### ✅ Obsidian as Dashboard
Using a simple folder-based vault (Inbox/Needs_Action/Done) provided:
- **Persistence:** Tasks survive system restarts
- **Visibility:** Human can read/edit any task
- **Audit Trail:** Complete history in Done/
- **Simplicity:** No database, just Markdown files

#### ✅ Ralph Wiggum Loop
The iterative completion pattern:
- Handled transient network failures
- Allowed multi-step task refinement
- Provided clear success/failure states
- Made debugging easier (see iteration count)

#### ✅ Playwright Browser Automation
Far more reliable than APIs for social platforms:
- No API rate limits
- Works with platform UI changes
- Human-like behavior reduces detection
- Screenshots provide audit trail

#### ✅ Persistent Sessions
Storing browser sessions locally:
- No repeated logins (reduces detection)
- Faster execution
- Handles 2FA gracefully (login once)

---

### Challenges & Solutions

#### ⚠️ Playwright Reliable but LinkedIn Detection Issue

**Problem:** LinkedIn has sophisticated bot detection that occasionally flags automated sessions.

**Symptoms:**
- "Suspicious login attempt" warnings
- CAPTCHA challenges
- Temporary account restrictions

**Solutions Implemented:**
```python
# 1. Human-like delays
page.wait_for_timeout(random.uniform(1000, 3000))

# 2. Mouse movements
await page.mouse.move(random_x, random_y)

# 3. Persistent sessions (avoid repeated logins)
context = browser.new_context(
    storage_state="./linkedin_session/state.json"
)

# 4. Randomized intervals (not exactly 60s)
interval = 60 + random.randint(-10, 10)
```

**Remaining Issue:** Detection still occurs occasionally; manual intervention sometimes required.

---

#### ⚠️ Importance of Persistent Sessions

**Problem:** Repeated logins trigger security alerts and CAPTCHAs.

**Solution:**
```python
# Save session after successful login
context.storage_state(path="./session/state.json")

# Reuse session on next run
context = browser.new_context(storage_state="./session/state.json")
```

**Lesson:** Session persistence is critical for production reliability.

---

#### ⚠️ Timeout and Slow Internet Handling

**Problem:** Slow connections cause premature timeouts and failures.

**Solutions:**
```python
# 1. Increased default timeouts
context = browser.new_context(
    timeout=60000,  # 60s instead of 30s
)

# 2. Explicit waits for elements
await page.wait_for_selector('.post-button', timeout=30000)

# 3. Retry with exponential backoff
for attempt in range(3):
    try:
        return action()
    except TimeoutError:
        time.sleep(2 ** attempt)
```

**Lesson:** Assume slow internet; build in generous timeouts.

---

#### ⚠️ Indentation and venv Issues

**Problem:** Python indentation errors and virtual environment confusion caused deployment failures.

**Solutions:**
```bash
# 1. Consistent venv setup
python3.13 -m venv .venv
source .venv/bin/activate

# 2. Requirements pinning
pip install -r requirements.txt

# 3. Pre-commit linting
flake8 --max-line-length=100 *.py
```

**Lesson:** Document venv setup clearly; use linting tools.

---

#### ⚠️ Why API Integration Was Skipped

**Decision:** Browser automation (Playwright) over official APIs.

**Reasons:**

| Factor | API Approach | Browser Approach |
|--------|--------------|------------------|
| **Detection** | Easy to detect and rate-limit | Harder to detect (looks human) |
| **Complexity** | OAuth, app approval, quotas | Simple: just automate browser |
| **Features** | Limited by API endpoints | Full UI access (all features) |
| **Setup Time** | Days/weeks for approval | Minutes |
| **Maintenance** | API version changes | UI changes (less frequent) |

**Specific Issues:**
- LinkedIn API: Requires company verification, limited posting capabilities
- Facebook API: App review process takes weeks
- Twitter API: Free tier severely limited
- Instagram API: Business account required, limited actions

**Conclusion:** Browser automation was the only viable hackathon approach.

---

### Improvements for Future Versions

#### 🔮 Web Dashboard
Replace Obsidian vault with a real web UI:
- Real-time task status
- Approval interface
- Analytics and metrics
- Mobile-friendly

#### 🔮 Better Anti-Detection
- Residential proxy rotation
- Browser fingerprint randomization
- More sophisticated human behavior simulation
- CAPTCHA solving integration

#### 🔮 Real MCP Implementation
- Proper MCP protocol compliance
- Server discovery and registration
- Standardized tool definitions
- Multi-model support

#### 🔮 Additional Platforms
- TikTok automation
- YouTube Shorts posting
- Reddit engagement
- Slack/Discord monitoring

#### 🔮 Advanced Reasoning
- Fine-tuned local model for classification
- Multi-agent collaboration
- Learning from past decisions
- Predictive task prioritization

---

## Conclusion: The Digital FTE

### Why This Is a True Digital Employee

| Attribute | Human Employee | AI Employee |
|-----------|----------------|-------------|
| **Hours/Week** | 40 | 168 (24/7/365) |
| **Sleep** | 8 hours/day | Never |
| **Sick Days** | ~10 days/year | 0 |
| **Vacation** | 2-4 weeks/year | 0 |
| **Multitasking** | Limited | Unlimited |
| **Consistency** | Variable | 100% |
| **Scaling** | Hire more | Copy/paste |
| **Cost** | $50k-$150k/year | ~$50/month (infra) |

### The 168 vs 40 Hour Advantage

A human works **40 hours/week** (8 hours × 5 days).  
This AI Employee works **168 hours/week** (24 hours × 7 days).

**That's 4.2× more coverage at ~1% of the cost.**

### Real-World Impact

**Before (Human-only):**
- Messages wait hours for response
- Social posts scheduled manually
- Weekly reports take hours to compile
- Tasks fall through cracks

**After (AI Employee):**
- Messages processed in <60 seconds
- Posts published instantly on approval
- Weekly briefings auto-generated
- Complete audit trail of everything

### Final Thoughts

This system represents a **paradigm shift** from:
- ❌ "Automation scripts" → ✅ "Digital employees"
- ❌ "Task-based" → ✅ "Role-based"
- ❌ "Scheduled" → ✅ "Continuous"
- ❌ "Siloed" → ✅ "Integrated"

The combination of **Claude Code reasoning**, **Playwright reliability**, **Obsidian persistence**, and the **Ralph Wiggum loop** creates something greater than the sum of its parts: a true **autonomous FTE** that works while you sleep.

---

*"Me fail English? That's unpossible!"* — Ralph Wiggum, probably while this system completes tasks in the background.

---

**Generated:** 2026-02-21  
**System:** Personal AI Employee Vault (Gold Tier)  
**Location:** `ARCHITECTURE.md`
