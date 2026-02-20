# LinkedIn Automation Agent - Silver Tier

Complete LinkedIn automation system for posting, monitoring, and scheduling.

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `setup_sessions.py` | One-time LinkedIn authentication |
| `linkedin_watcher.py` | Monitor messages & notifications |
| `linkedin_poster.py` | Create and publish posts |
| `linkedin_manager.py` | Combined post + watch |
| `linkedin_simple.py` | Simple unified interface |
| `linkedin_scheduler.py` | Auto-post at optimal times |
| `Skills/linkedin_processing.md` | Processing documentation |

---

## 🚀 Quick Start

### First Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browser
playwright install chromium

# 3. Setup LinkedIn session (opens browser for login)
python setup_sessions.py
```

### Daily Use

```bash
# Test setup
python linkedin_simple.py test

# Post content
python linkedin_simple.py post -c "Hello LinkedIn! #automation"

# Watch for messages
python linkedin_simple.py watch

# Run scheduler (auto-posts)
python linkedin_scheduler.py

# Test scheduler (post now)
python linkedin_scheduler.py test
```

---

## 📋 Commands Reference

### Setup Sessions
```bash
python setup_sessions.py
```
Opens browser for manual LinkedIn login. Saves session for future use.

### LinkedIn Simple (Recommended)
```bash
# Test
python linkedin_simple.py test

# Post
python linkedin_simple.py post -c "Your content here"
python linkedin_simple.py post -f post.txt

# Watch
python linkedin_simple.py watch
```

### LinkedIn Poster
```bash
python linkedin_poster.py -c "Post content"
python linkedin_poster.py --file content.txt
python linkedin_poster.py --visible  # Show browser
```

### LinkedIn Watcher
```bash
python linkedin_watcher.py
```
Monitors messages and notifications. Saves to `./Inbox/`.

### LinkedIn Manager
```bash
python linkedin_manager.py post -c "Content"
python linkedin_manager.py watch
python linkedin_manager.py both -c "Content"
```

### LinkedIn Scheduler
```bash
python linkedin_scheduler.py        # Run scheduled posts
python linkedin_scheduler.py test   # Post immediately (test)
```

---

## ⏰ Scheduler - Optimal Posting Times

| Day | Time |
|-----|------|
| Tuesday | 9:00 AM, 12:00 PM |
| Wednesday | 9:00 AM |
| Thursday | 9:00 AM, 12:00 PM |
| Friday | 5:00 PM |

---

## 🔐 Configuration

### Environment Variables (.env file)

```bash
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=yourpassword
```

### Session Storage

Sessions saved to: `./linkedin_session/storage_state.json`

If session expires, re-run:
```bash
python setup_sessions.py
```

---

## 📂 Directory Structure

```
phase2_silver/
├── setup_sessions.py          # Session setup
├── linkedin_watcher.py        # Message watcher
├── linkedin_poster.py         # Post creator
├── linkedin_manager.py        # Combined manager
├── linkedin_simple.py         # Simple interface
├── linkedin_scheduler.py      # Auto scheduler
├── .env                       # Credentials (create this)
├── requirements.txt           # Dependencies
├── Skills/
│   └── linkedin_processing.md # Processing docs
├── Inbox/                     # New messages/notifications
├── Needs_Action/              # Tasks requiring action
├── Logs/                      # Activity logs
└── linkedin_session/          # Saved session data
```

---

## ⚠️ Important Rules

1. **NO credentials in code** - Use `.env` file only
2. **Check session before running** - Run `setup_sessions.py` if expired
3. **Don't close browser during setup** - Wait for ENTER prompt
4. **Headless mode** - `True` for watcher, `False` for debugging
5. **Auto-directories** - All folders created automatically

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| No session found | Run `python setup_sessions.py` |
| Login failed | Check credentials in `.env` |
| Browser won't open | Run `playwright install chromium` |
| Session expired | Re-run `setup_sessions.py` |
| Post not publishing | Use `--visible` flag to debug |

---

## 📊 Sample Posts

```
🚀 Excited to share my latest project! Building automation tools 
   that save time. #Automation #Tech

💡 Tip: Automate repetitive tasks to focus on what matters.
   #ProductivityTips #WorkSmart

🎯 Goal setting is about the systems you build, not just the
   destination. #Goals #Success #Mindset
```

---

## 📝 Workflow

```
1. Run setup_sessions.py (first time only)
   ↓
2. Browser opens → Login to LinkedIn → Press ENTER
   ↓
3. Session saved to linkedin_session/
   ↓
4. Use any LinkedIn script:
   - linkedin_simple.py post    (create post)
   - linkedin_simple.py watch   (monitor)
   - linkedin_scheduler.py      (auto-post)
   ↓
5. New messages saved to Inbox/
   ↓
6. Process with linkedin_processing.md skill
```

---

## 🛠️ Dependencies

```
playwright==1.44.0
schedule==1.2.1
python-dotenv
```

Install:
```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 📞 Support

For issues:
1. Check `./Logs/` for error messages
2. Run with `--visible` to see browser actions
3. Verify session: `python linkedin_simple.py test`
4. Re-authenticate: `python setup_sessions.py`

---

*LinkedIn Automation Agent - Silver Tier*
*All work in phase2_silver only - phase1_bronze untouched*
