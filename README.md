# AI Employee Vault - Complete Testing Guide

## Pre-Testing Setup

### Step 1: Install Dependencies
```bash
cd /mnt/c/Users/user/Desktop/AI_Employee_Vault/phase3_gold
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

### Step 2: Configure Environment
```bash
cp .env.example .env
nano .env  # Add your credentials
```

---

## Phase 1 Bronze - File Watcher Test

**Terminal 1:**
```bash
cd ../phase1_bronze/
timeout 15s python3 Watchers/inbox_watcher.py
```

**Terminal 2:**
```bash
cd ../phase1_bronze/
echo "# Test Task" > Inbox/test.md
```

---

## Phase 2 Silver - Watchers Test

```bash
cd ../phase2_silver/Watchers/
python gmail_watcher.py
python inbox_watcher.py
```

---

## Phase 3 Gold - Full System Test

```bash
cd ../phase3_gold/
source .venv/bin/activate

# Test watchers
python twitter_browser_watcher.py
python fb_ig_browser_watcher.py

# Test orchestrator
python ai_orchestrator.py

# Test audit
python weekly_audit.py
```

---

## MCP Servers Test

```bash
# Start servers
node social_mcp.js &
python audit_mcp.py &

# Test health
curl http://localhost:3000/health
curl http://localhost:3001/health

# Stop servers
pkill -f social_mcp.js
pkill -f audit_mcp.py
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | pip install -r requirements.txt |
| Playwright missing | playwright install |
| Login failures | Check .env credentials |
| Port in use | pkill -f social_mcp.js |

---

**Version:** 1.0.0 | **Status:** Gold Tier Production Ready
