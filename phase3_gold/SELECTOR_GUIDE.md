# Selector Configuration Guide

## Problem Solved ✅

**Before:** Website selectors change → Code breaks → Need to edit Python files

**After:** Website selectors change → Update `selectors.json` → Done!

---

## Quick Start

### When Login/Posting Stops Working

1. **Run the update utility:**
   ```bash
   python update_selectors.py
   ```

2. **Select the platform** (Twitter/Facebook/Instagram)

3. **Update the broken selector** with new value from browser DevTools

4. **Save and re-run** your poster script

---

## File Structure

```
phase3_gold/
├── selectors.json          # ← Edit this when selectors change
├── selector_loader.py      # ← Loads selectors (don't edit)
├── update_selectors.py     # ← Interactive update tool
├── twitter_auto_poster.py  # ← Uses selectors.json
├── fb_poster.py            # ← Uses selectors.json
├── instagram_auto_poster.py# ← Uses selectors.json
└── fb_ig_poster.py         # ← Uses selectors.json
```

---

## How to Find New Selectors

### Using Browser DevTools

1. Open browser (Chrome/Edge)
2. Go to the website (twitter.com, facebook.com, instagram.com)
3. Press `F12` to open DevTools
4. Click the **Selector tool** (top-left corner of DevTools)
5. Click on the element you need (login button, input field, etc.)
6. Right-click the highlighted HTML → Copy → Copy selector

### Example Selectors

**Input Fields:**
```
input[name="username"]
input[type="password"]
input[autocomplete="username"]
```

**Buttons:**
```
button:has-text("Log in")
button[name="login"]
[role="button"]:has-text("Next")
```

**Content Areas:**
```
[aria-label="What's on your mind?"]
[data-testid="tweetTextarea_0"]
article[role="article"]
```

---

## selectors.json Format

```json
{
  "twitter": {
    "username_field": "input[autocomplete='username']",
    "password_field": "input[type='password']",
    "login_button": ["Log in", "Log In"],
    "tweet_box": "[data-testid='tweetTextarea_0']",
    "post_button": ["Post", "Tweet"]
  },
  "timeouts": {
    "page_load": 60000,
    "selector_wait": 15000
  },
  "delays": {
    "human_min": 500,
    "human_max": 2000
  }
}
```

### Key Types

| Key | Type | Example |
|-----|------|---------|
| `_field` | String (CSS selector) | `"input[name='email']"` |
| `_button` | Array (text patterns) | `["Log in", "Continue"]` |
| `timeout` | Integer (milliseconds) | `60000` |
| `delay` | Integer (milliseconds) | `500` |

---

## Common Issues & Fixes

### Issue: "Email field not found"
**Fix:** Update `email_field` selector in `selectors.json`

### Issue: "Login button not found"
**Fix:** Update `login_button` array with new button text

### Issue: "Timeout waiting for feed"
**Fix:** Increase `feed_wait` timeout or update `home_feed` selector

### Issue: "Post button not found"
**Fix:** Update `post_button` array with new button text

---

## Testing New Selectors

1. Update selector in `selectors.json`
2. Run validation:
   ```bash
   python selector_loader.py
   ```
3. Test the script:
   ```bash
   python twitter_auto_poster.py
   ```

---

## Backup Selectors

Keep a backup of working selectors:

```bash
cp selectors.json selectors_backup.json
```

Restore if needed:
```bash
cp selectors_backup.json selectors.json
```

---

## For Advanced Users

### Programmatic Update

```python
from selector_loader import update_selector

# Update Twitter login button
update_selector('twitter', 'login_button', ['Sign in', 'Log in'])

# Update timeout
update_selector('timeouts', 'feed_wait', 45000)
```

### Load Selectors in Custom Scripts

```python
from selector_loader import get_selector, get_timeout

# Get selector
username_selector = get_selector('twitter', 'username_field')

# Get timeout
timeout = get_timeout('selector_wait', 15000)
```

---

## Best Practices

1. ✅ **Test selectors in browser first** using DevTools console
2. ✅ **Use multiple fallback selectors** in arrays
3. ✅ **Keep selectors specific** but not too fragile
4. ✅ **Document changes** in selectors.json comments
5. ✅ **Backup working configurations**

---

## Support

If selectors keep breaking frequently:
- Consider using **official APIs** (Twitter API, Facebook Graph API)
- Check if website has **anti-bot protection**
- Verify your **account status** (not flagged/suspended)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-24 | Initial dynamic selector system |
