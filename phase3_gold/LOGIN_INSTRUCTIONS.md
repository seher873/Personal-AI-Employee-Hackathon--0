# Login Instructions / لاگن ہدایات

## Problem / مسئلہ
Headless browser mein aap **dekh nahi sakte** isliye login nahi kar pa rahe!

## Solution / حل

### Option 1: Windows se Login (Recommended)

1. **Open Windows PowerShell** and run:
```powershell
cd C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold
.\.venv\Scripts\Activate.ps1
python login_browser.py --platform all
```

2. **Browser window will open** - Login manually
3. **After login**, session will be saved
4. **Restart watchers** in WSL

### Option 2: Use Existing Browser Session

1. Open **Chrome/Edge** on Windows
2. Login to:
   - https://facebook.com
   - https://instagram.com  
   - https://twitter.com
3. Export cookies (use extension like "EditThisCookie")
4. Copy to session folders

### Option 3: Run Watchers with Visible Browser

For testing only (not for production):

```bash
# Stop current watchers
pkill -f browser_watcher

# Run with visible browser (need X server)
xvfb-run python3 fb_ig_browser_watcher.py --platform both
xvfb-run python3 twitter_browser_watcher.py
```

## Current Status / موجودہ حیثیت

- ✅ Watchers running (headless)
- ✅ English language enabled
- ✅ Credentials configured
- ❌ **Login pending** (need manual intervention)

## After Login / لاگن کے بعد

Watchers will automatically:
- Check messages every 60 seconds
- Save new items to Inbox/
- Auto-relogin if session expires
