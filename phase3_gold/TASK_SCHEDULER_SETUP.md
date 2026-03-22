# Windows Task Scheduler Setup Guide

Automated scheduling for AI Employee Gold Tier skills.

---

## 📋 Schedule Overview

| Task | Frequency | Time | Script |
|------|-----------|------|--------|
| Daily Posts | Every Day | 9:00 AM | `run_daily_posts.bat` |
| Hourly Check | Every Hour | :00 | `run_hourly_check.bat` |
| Weekly Audit | Every Friday | 5:00 PM | `run_weekly_audit.bat` |

---

## 🔧 Setup Instructions

### Step 1: Open Task Scheduler

1. Press `Win + R`
2. Type: `taskschd.msc`
3. Press Enter

---

### Step 2: Create Basic Task - Daily Posts

1. **Right-click** "Task Scheduler Library" → **"Create Basic Task..."**

2. **Name:** `AI Employee - Daily Social Posts`
   **Description:** Posts to Facebook, Instagram, Twitter daily at 9 AM
   **Next**

3. **Trigger:** Select **"Daily"**
   **Next**

4. **Start:** `9:00:00 AM`
   **Recur every:** `1` days
   **Next**

5. **Action:** Select **"Start a program"**
   **Next**

6. **Program/script:** Browse and select:
   ```
   C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold\run_daily_posts.bat
   ```

7. **Start in (optional):**
   ```
   C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold
   ```
   **Next**

8. **Finish**

---

### Step 3: Create Basic Task - Hourly Check

1. **Right-click** "Task Scheduler Library" → **"Create Basic Task..."**

2. **Name:** `AI Employee - Hourly Message Check`
   **Description:** Checks WhatsApp and Gmail every hour
   **Next**

3. **Trigger:** Select **"One time"**
   **Next**

4. **Start:** Set to next hour (e.g., 2:00:00 PM)
   **Next**

5. **Action:** Select **"Start a program"**
   **Next**

6. **Program/script:** Browse and select:
   ```
   C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold\run_hourly_check.bat
   ```

7. **Start in (optional):**
   ```
   C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold
   ```
   **Next**

8. **Finish**

9. **NOW Configure Repeat:**
   - Right-click the new task → **Properties**
   - **Triggers** tab → Select trigger → **Edit**
   - Check **"Repeat task every:"** → Select **"1 hour"**
   - Check **"for a duration of:"** → Select **"Indefinitely"**
   - **OK**

---

### Step 4: Create Basic Task - Weekly Audit

1. **Right-click** "Task Scheduler Library" → **"Create Basic Task..."**

2. **Name:** `AI Employee - Weekly Audit`
   **Description:** Generates weekly report and CEO briefing
   **Next**

3. **Trigger:** Select **"Weekly"**
   **Next**

4. **Start:** `5:00:00 PM`
   **Recur every:** `1` weeks
   **Check:** `Friday`
   **Next**

5. **Action:** Select **"Start a program"**
   **Next**

6. **Program/script:** Browse and select:
   ```
   C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold\run_weekly_audit.bat
   ```

7. **Start in (optional):**
   ```
   C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold
   ```
   **Next**

8. **Finish**

---

## ⚙️ Advanced Settings (Recommended)

For each task, configure these settings:

1. Right-click task → **Properties**

2. **General tab:**
   - ✅ **Run whether user is logged on or not**
   - ✅ **Run with highest privileges**
   - **Configure for:** Windows 10 (or your version)

3. **Conditions tab:**
   - ✅ **Start only if on AC power** (for laptops)
   - ❌ **Stop if computer switches to battery** (uncheck)

4. **Settings tab:**
   - ✅ **Allow task to be run on demand**
   - ✅ **Run task as soon as possible after scheduled start is missed**
   - ✅ **If task fails, restart every:** `5 minutes`
   - **Attempt to restart:** `3` times

---

## ✅ Verify Tasks

1. Open Task Scheduler
2. Click **"Task Scheduler Library"**
3. You should see:
   ```
   - AI Employee - Daily Social Posts
   - AI Employee - Hourly Message Check
   - AI Employee - Weekly Audit
   ```

4. **Check "Last Run Time"** and **"Next Run Time"** columns

---

## 🧪 Test Tasks

### Manual Test:

1. Right-click task → **Run**
2. Check logs in `./Logs/` folder
3. Verify output

### Check Results:

```bash
# After running Daily Posts
dir Logs\*poster*.log

# After running Hourly Check
dir Logs\*watcher*.log
dir Inbox\

# After running Weekly Audit
dir Reports\
```

---

## 🔧 Troubleshooting

### Task doesn't run:
1. Check **History** tab in Task Scheduler
2. Verify `.bat` file path is correct
3. Ensure "Start in" folder is set

### Task runs but scripts fail:
1. Check `py` command works in terminal
2. Verify `.env` credentials are set
3. Check logs in `./Logs/`

### Permission errors:
1. Right-click task → Properties
2. Check **"Run with highest privileges"**
3. Enter admin password if prompted

---

## 📊 View Task History

1. Open Task Scheduler
2. Click on task name
3. Click **"History"** tab
4. See all run attempts and results

---

## 🗑️ Disable/Remove Tasks

### Temporarily Disable:
1. Right-click task → **Disable**

### Permanently Remove:
1. Right-click task → **Delete**

---

## 📝 Schedule Summary

```
┌─────────────────────────────────────────────────────┐
│           AI Employee - Task Schedule               │
├─────────────────────────────────────────────────────┤
│  DAILY POSTS (9:00 AM)                              │
│  ├─ Facebook Post                                   │
│  ├─ Instagram Post                                  │
│  └─ Twitter Post                                    │
├─────────────────────────────────────────────────────┤
│  HOURLY CHECK (Every Hour)                          │
│  ├─ WhatsApp Messages                               │
│  └─ Gmail Messages                                  │
├─────────────────────────────────────────────────────┤
│  WEEKLY AUDIT (Friday 5:00 PM)                      │
│  ├─ Generate Weekly Report                          │
│  └─ CEO Briefing                                    │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Setup Complete!

After setup:
- ✅ Daily posts run automatically at 9 AM
- ✅ Message checks run every hour
- ✅ Weekly audit runs Friday 5 PM
- ✅ All results logged to `./Logs/`

---

**Version:** Gold Tier 1.0
**Last Updated:** 2026-03-01
