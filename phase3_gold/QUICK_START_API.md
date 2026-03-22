# 🚀 API-Based Social Media Posting - Quick Start

## ✅ Setup Complete!

Your Facebook, Instagram, and WhatsApp API credentials have been configured.

---

## 📝 What You Provided

```
Facebook Access Token: EAALGYQr6X3ABQ1KOvWe2ooNt9D0VcZCYTofB0SDqFSNCqePBZCFUXmFAvNJ1M8CQAvBavwRvJPheQdgbMgMJUzpzU4AOZCV6WG3IGOOZCrVGoGH0mqd1EnZAkXxOEULGOA0nmlhBpAZCgXZAGLecsBWBiKNWO3J8tQwRNaZBFDxPq8ZCqXuLkPwCHWxLzokvBHZCsbP31zZAfPx80KWX1ueZAvVPPhUMdsTGpPUjxhlS0DEAX2tnZBJijpDGhfLHt0EakTNvrZBgSJtZBlZB7JZC8ntdYFiBZCd81Q
Facebook Page ID: 61583823080924
Instagram ID: 17841447308298408
```

All credentials are now saved in `.env` file.

---

## 🎯 Quick Commands

### 1️⃣ Test Your Setup (Recommended First Step)

```bash
test_api.bat
```

This verifies your API tokens are working correctly.

### 2️⃣ Make a Test Post

```bash
quick_test.bat
```

This posts a test message to Facebook and Instagram.

### 3️⃣ Post Custom Content

**Facebook only:**
```bash
py social_post_watcher.py --post "Your message here"
```

**Facebook + Instagram with image:**
```bash
py social_post_watcher.py --post "Your message" --image "path/to/image.png" --platforms facebook instagram
```

**With WhatsApp:**
```bash
py social_post_watcher.py --post "Your message" --whatsapp-to +1234567890
```

### 4️⃣ Automated Posting (Watch Mode)

```bash
run_social_watcher.bat
```

This continuously monitors the `./Inbox` folder for new posts.

---

## 📁 New Files Created

| File | Purpose |
|------|---------|
| `.env` | Your API credentials (configured ✅) |
| `social_post_watcher.py` | Main posting script |
| `test_api_credentials.py` | Test API tokens |
| `quick_test_post.py` | Quick test post |
| `Skills/skill_facebook_api.py` | Facebook API integration |
| `Skills/skill_instagram_api.py` | Instagram API integration |
| `Skills/skill_whatsapp_api.py` | WhatsApp API integration |
| `API_POSTING_GUIDE.md` | Full documentation |
| `API_SETUP_COMPLETE.md` | Detailed setup guide |

---

## 🔧 Important Notes

### Instagram Images

Instagram requires **public URLs** for images (not local file paths).

**Options:**
1. Upload to cloud storage (Google Drive, Dropbox, S3)
2. Use a web server
3. Use browser-based posting (`skill_instagram.py`) as fallback

### Token Expiry

Facebook tokens expire. If posting fails:
1. Visit: https://developers.facebook.com/tools/explorer/
2. Generate new token with permissions: `pages_manage_posts`, `instagram_content_publish`
3. Update `.env` file

### WhatsApp (Optional)

WhatsApp not configured yet. Add to `.env` if needed:
```env
WHATSAPP_PHONE=your_phone_number_id
WHATSAPP_API_KEY=your_api_key
```

---

## 📊 Logs & Monitoring

All activity is logged to:
- `./Logs/social_watcher_audit.jsonl` - Complete audit trail
- `./Logs/facebook_api_*.log` - Facebook logs
- `./Logs/instagram_api_*.log` - Instagram logs
- `./Logs/whatsapp_api_*.log` - WhatsApp logs

---

## ❓ Troubleshooting

**Problem:** "Invalid access token"
- **Solution:** Generate new token at Facebook Developer Explorer

**Problem:** "Instagram ID not found"
- **Solution:** Ensure Instagram is a Business account connected to your FB Page

**Problem:** "Image URL not accessible"
- **Solution:** Use public URL or cloud storage for Instagram images

---

## 📚 Documentation

- **Full Guide:** `API_POSTING_GUIDE.md`
- **Setup Details:** `API_SETUP_COMPLETE.md`
- **Config Reference:** `config.py`

---

## ✨ Benefits Over Browser Automation

| Feature | Old (Playwright) | New (API) |
|---------|------------------|-----------|
| Reliability | ⚠️ UI changes break it | ✅ Stable |
| Speed | 🐌 Slow | ⚡ Fast |
| Login Issues | ❌ Common | ✅ None |
| Session Management | 🔧 Manual | ✅ Automatic |

---

## 🎉 You're Ready!

Run `test_api.bat` to verify everything works, then start posting!

For questions or issues, check the logs in `./Logs/` directory.

---

**Created for Phase 3 Gold - AI Employee Vault**
*No more Playwright issues on Facebook/Instagram! 🚀*
