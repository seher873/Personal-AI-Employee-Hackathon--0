# LinkedIn API Setup Guide

## Overview

AI Employee ab **LinkedIn Official API** use karta hai - browser automation ki jagah. Ye zyada secure, fast aur reliable hai.

## Benefits: API vs Browser

| Browser Automation | Official API |
|-------------------|--------------|
| Login required | No login (tokens) |
| Bot detection risk | Official method |
| Slow | Fast |
| UI changes break it | Stable |
| Session management needed | Stateless |

---

## Setup Complete ✅

Aapke credentials already `.env` file mein configure hain:

```env
LINKEDIN_CLIENT_ID=YOUR_CLIENT_ID
LINKEDIN_CLIENT_SECRET=YOUR_CLIENT_SECRET
LINKEDIN_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
COMPANY_URN=urn:li:organization:YOUR_COMPANY_ID
```

---

## Files Created

1. **`Skills/skill_linkedin_api.py`** - Main LinkedIn API skill
2. **`test_linkedin_api.py`** - Connection test script
3. **`mcp_servers/mcp_server_social.js`** - Updated with `/post-linkedin` endpoint
4. **`config.py`** - Updated with LinkedIn credential support

---

## Test Connection

```bash
# Test API connection
python test_linkedin_api.py
```

Expected output:
```
✓ LinkedIn API credentials loaded
✓ Connected as: Your Name
✓ Company: Your Company
```

---

## Usage Examples

### 1. Direct Python API Call

```python
from Skills.skill_linkedin_api import LinkedInAPIClient

client = LinkedInAPIClient()

# Post text only
client.post_text("Hello from AI Employee! #Automation")

# Post to company page
client.post_text("Company announcement", company=True)

# Post with image
client.post_with_image("Check this out!", "path/to/image.jpg")
```

### 2. Via MCP Server (HTTP API)

```bash
# Start MCP server
node mcp_servers/mcp_server_social.js

# Post to LinkedIn
curl -X POST http://localhost:3000/post-linkedin \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from AI Employee!", "company": false}'
```

### 3. Post to All Platforms

```bash
curl -X POST http://localhost:3000/post-all \
  -H "Content-Type: application/json" \
  -d '{"text": "Cross-platform post!", "image_path": "image.jpg"}'
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/post-linkedin` | POST | Post to LinkedIn |
| `/post-all` | POST | Post to all platforms (incl. LinkedIn) |
| `/health` | GET | Server health check |
| `/stats` | GET | Server statistics |

---

## Troubleshooting

### Token Expired

```
Error: 401 Unauthorized
```

**Solution:** Generate new access token from LinkedIn Developer Dashboard

### Credentials Not Found

```
Error: LINKEDIN_CLIENT_ID not found in .env
```

**Solution:** Check `.env` file has correct credentials

### Company Page Not Accessible

```
Error: 403 Forbidden
```

**Solution:** Verify COMPANY_URN is correct and you have admin access

---

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` file to Git
- Rotate tokens periodically
- Use app passwords where possible
- Keep `credentials.json` out of version control

---

## Next Steps

1. ✅ Test connection: `python test_linkedin_api.py`
2. ✅ Try a test post (uncomment test code)
3. ✅ Integrate with AI Employee workflow
4. ✅ Monitor Audit_Log.md for posts

---

## API Documentation

- [LinkedIn API Reference](https://learn.microsoft.com/en-us/linkedin/consumer/integrations)
- [UGC Posts API](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [Organizations API](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/organizations-api)
