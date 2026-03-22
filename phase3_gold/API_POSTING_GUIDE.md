# API-Based Social Media Posting

## Overview

This module provides **API-based** posting to Facebook, Instagram, and WhatsApp, eliminating the browser automation issues with Playwright.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials (.env file)

Your `.env` file has been updated with the following credentials:

```env
# Facebook API
FB_ACCESS_TOKEN=EAALGYQr6X3ABQ1KOvWe2ooNt9D0VcZCYTofB0SDqFSNCqePBZCFUXmFAvNJ1M8CQAvBavwRvJPheQdgbMgMJUzpzU4AOZCV6WG3IGOOZCrVGoGH0mqd1EnZAkXxOEULGOA0nmlhBpAZCgXZAGLecsBWBiKNWO3J8tQwRNaZBFDxPq8ZCqXuLkPwCHWxLzokvBHZCsbP31zZAfPx80KWX1ueZAvVPPhUMdsTGpPUjxhlS0DEAX2tnZBJijpDGhfLHt0EakTNvrZBgSJtZBlZB7JZC8ntdYFiBZCd81Q
FB_PAGE_ID=61583823080924

# Instagram API
IG_ID=17841447308298408

# WhatsApp API (optional)
WHATSAPP_PHONE=
WHATSAPP_API_KEY=
```

### 3. Test Your Credentials

```bash
py test_api_credentials.py
```

This will verify that your API tokens are valid and working.

## Usage

### Quick Post to All Platforms

```bash
py social_post_watcher.py --post "Hello from AI Employee!" --image "post_image.png"
```

### Post to Specific Platforms

```bash
py social_post_watcher.py --post "Hello World!" --platforms facebook instagram --image "post_image.png"
```

### Watch Mode (Continuous Monitoring)

```bash
py social_post_watcher.py --watch --interval 60
```

This watches the `./Inbox` directory for `.post` files and automatically publishes them.

### Create a Post File

Create a file in `./Inbox/` with `.post` extension:

```json
{
  "text": "Check out our new product!",
  "image": "C:/path/to/image.png",
  "platforms": ["facebook", "instagram"],
  "whatsapp_recipients": ["+1234567890", "+0987654321"]
}
```

The watcher will automatically process it and rename it to `.processed`.

### Send WhatsApp Message Only

```bash
py social_post_watcher.py --post "Your invoice is ready!" --whatsapp-to +1234567890
```

### View Statistics

```bash
py social_post_watcher.py --stats
```

## Skills

Three new API-based skills have been created:

- `Skills/skill_facebook_api.py` - Facebook Graph API posting
- `Skills/skill_instagram_api.py` - Instagram Graph API posting
- `Skills/skill_whatsapp_api.py` - WhatsApp Business API messaging

### Example: Use Skills Directly

```python
from Skills.skill_facebook_api import FacebookAPISkill

fb = FacebookAPISkill()
result = fb.post("Hello from API!", "image.png")
print(result)
```

```python
from Skills.skill_instagram_api import InstagramAPISkill

ig = InstagramAPISkill()
result = ig.post("Instagram post!", "image.png")
print(result)
```

```python
from Skills.skill_whatsapp_api import WhatsAppAPISkill

wa = WhatsAppAPISkill()
result = wa.send_message("+1234567890", "Hello!")
print(result)
```

## Batch File

Quick start with the batch file:

```bash
run_social_watcher.bat
```

## Important Notes

### Instagram Image Requirement

Instagram API **requires** images to be publicly accessible URLs. For local images, you have two options:

1. **Host images on a server** (recommended for production)
2. **Use the browser-based skill** (`skill_instagram.py`) for local images

### Facebook Page Access Token

Your access token must have these permissions:
- `pages_manage_posts`
- `pages_read_engagement`
- `instagram_basic`
- `instagram_content_publish`

### Token Expiry

Facebook access tokens expire. If posting fails, generate a new token from:
https://developers.facebook.com/tools/explorer/

### WhatsApp Setup

For WhatsApp, you need:
1. WhatsApp Business Account
2. Phone Number ID
3. API Key (from Meta Developer Console)

## Troubleshooting

### "Invalid Access Token"

- Token may have expired - generate a new one
- Token permissions may be insufficient

### "Instagram ID not found"

- Ensure your Instagram account is a Business account
- Connect it to your Facebook Page

### "Image URL not accessible" (Instagram)

- Image must be at a public URL
- Consider using cloud storage (S3, Cloudinary, etc.)

### "WhatsApp credentials not configured"

- Set `WHATSAPP_PHONE` and `WHATSAPP_API_KEY` in `.env`
- These are optional - leave blank if not using WhatsApp

## Logs

All posts are logged to:
- `./Logs/social_watcher_audit.jsonl` - Audit trail
- `./Logs/facebook_api_*.log` - Facebook logs
- `./Logs/instagram_api_*.log` - Instagram logs
- `./Logs/whatsapp_api_*.log` - WhatsApp logs

## Migration from Browser-based Posting

The API-based approach is **more reliable** than browser automation:

| Feature | Browser (Playwright) | API-based |
|---------|---------------------|-----------|
| Reliability | ⚠️ Can break with UI changes | ✅ Stable |
| Speed | 🐌 Slower (loads browser) | ⚡ Fast |
| Session Management | 🔧 Requires maintenance | ✅ None needed |
| Image Upload | ✅ Works locally | ⚠️ Needs URL |
| Comments/Replies | ✅ Full interaction | ⚠️ API limited |

**Recommendation**: Use API-based for posting, keep browser-based as backup.

## Next Steps

1. ✅ Test credentials: `py test_api_credentials.py`
2. ✅ Make a test post: `py social_post_watcher.py --post "Test"`
3. ✅ Set up watch mode for automated posting
4. ✅ Configure WhatsApp if needed

---

**Created for Phase 3 Gold - AI Employee Vault**
