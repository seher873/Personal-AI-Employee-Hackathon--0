# MCP Servers - Gold Tier Requirement #6

Multiple MCP (Model Context Protocol) servers for AI Employee automation.

---

## 📋 Server Overview

| Server | Port | Protocol | Purpose |
|--------|------|----------|---------|
| **Social Media MCP** | 3000 | HTTP/REST | Facebook, Instagram, Twitter posting |
| **Audit MCP** | 3001 | HTTP/REST | Weekly audit, CEO briefing |
| **Communication MCP** | 3002 | HTTP/REST | WhatsApp, Gmail monitoring |
| **Email MCP** | 3003 | HTTP/REST | Send emails (Gold Tier Requirement) |

---

## 🚀 Quick Start

### 1. Social Media MCP (Node.js)

```bash
cd mcp_servers

# Install dependencies (first time only)
npm install

# Start server
node mcp_server_social.js
# Or use batch file
start_social_mcp.bat
```

**Test:**
```bash
curl http://localhost:3000/health
```

### 2. Audit MCP (Python)

```bash
cd mcp_servers

# Start server
py mcp_server_audit.py
# Or use batch file
start_audit_mcp.bat
```

**Test:**
```bash
curl http://localhost:3001/health
```

### 3. Communication MCP (Python)

```bash
cd mcp_servers

# Start server
py mcp_server_communication.py
# Or use batch file
start_communication_mcp.bat
```

**Test:**
```bash
curl http://localhost:3002/health
```

---

## 📖 API Documentation

### Social Media MCP (Port 3000)

#### POST /post-fb
Post to Facebook

```bash
curl -X POST http://localhost:3000/post-fb \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from AI!", "image_path": "post_image.png"}'
```

#### POST /post-ig
Post to Instagram

```bash
curl -X POST http://localhost:3000/post-ig \
  -H "Content-Type: application/json" \
  -d '{"text": "Instagram post!", "image_path": "post_image.png"}'
```

#### POST /post-x
Post to Twitter/X (max 280 chars)

```bash
curl -X POST http://localhost:3000/post-x \
  -H "Content-Type: application/json" \
  -d '{"text": "Tweet from AI! #Automation"}'
```

#### POST /post-all
Post to all platforms

```bash
curl -X POST http://localhost:3000/post-all \
  -H "Content-Type: application/json" \
  -d '{"text": "Cross-platform post!", "image_path": "post_image.png"}'
```

#### GET /health
Health check

```bash
curl http://localhost:3000/health
```

#### GET /stats
Server statistics

```bash
curl http://localhost:3000/stats
```

---

### Audit MCP (Port 3001)

#### POST /generate_briefing
Generate CEO briefing

```bash
curl -X POST http://localhost:3001/generate_briefing
```

#### GET /briefing
Get current CEO briefing

```bash
curl http://localhost:3001/briefing
```

#### GET /vault-summary
Get summary of vault contents

```bash
curl http://localhost:3001/vault-summary
```

#### POST /audit
Run full audit

```bash
curl -X POST http://localhost:3001/audit
```

#### GET /health
Health check

```bash
curl http://localhost:3001/health
```

#### GET /stats
Server statistics

```bash
curl http://localhost:3001/stats
```

---

### Communication MCP (Port 3002)

#### POST /check-whatsapp
Check WhatsApp messages

```bash
curl -X POST http://localhost:3002/check-whatsapp
```

#### POST /check-gmail
Check Gmail messages

```bash
curl -X POST http://localhost:3002/check-gmail
```

#### GET /inbox
Get inbox contents

```bash
curl http://localhost:3002/inbox
```

#### GET /health
Health check

```bash
curl http://localhost:3002/health
```

---

### Email MCP (Port 3003)

#### POST /send-email
Send email

```bash
curl -X POST http://localhost:3003/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "ceo@example.com",
    "subject": "Weekly Report",
    "body": "Please find attached the weekly report.",
    "cc": "manager@example.com",
    "html": false
  }'
```

#### POST /send-briefing
Send CEO briefing via email

```bash
curl -X POST http://localhost:3003/send-briefing \
  -H "Content-Type: application/json" \
  -d '{
    "to": "ceo@example.com"
  }'
```

#### GET /health
Health check

```bash
curl http://localhost:3003/health
```

#### GET /stats
Server statistics

```bash
curl http://localhost:3003/stats
```

#### GET /stats
Server statistics

```bash
curl http://localhost:3002/stats
```

---

## 🔧 Start All Servers

### Windows Batch Script

Create `start_all_mcp.bat`:

```batch
@echo off
echo Starting all MCP servers...

REM Start Social Media MCP (Node.js)
start cmd /k "cd mcp_servers && node mcp_server_social.js"

REM Start Audit MCP (Python)
start cmd /k "cd mcp_servers && py mcp_server_audit.py"

REM Start Communication MCP (Python)
start cmd /k "cd mcp_servers && py mcp_server_communication.py"

REM Start Email MCP (Python)
start cmd /k "cd mcp_servers && py mcp_server_email.py"

echo All MCP servers started!
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│              AI Employee - Gold Tier                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   Facebook   │  │  Instagram   │  │  Twitter │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │
│         │                 │                │        │
│         └─────────────────┴────────────────┘        │
│                           │                         │
│                  ┌────────▼────────┐                │
│                  │  Social MCP     │                │
│                  │  Port: 3000     │                │
│                  └─────────────────┘                │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                │
│  │  WhatsApp    │  │    Gmail     │                │
│  └──────┬───────┘  └──────┬───────┘                │
│         │                 │                         │
│         └─────────────────┴────────────────┐        │
│                                           ▼        │
│                                  ┌─────────────────┐│
│                                  │Communication MCP││
│                                  │  Port: 3002     ││
│                                  └─────────────────┘│
│                                                     │
│  ┌────────────────────────────────┐                 │
│  │      Weekly Audit + CEO        │                 │
│  └────────────┬───────────────────┘                 │
│               │                                     │
│               ▼                                     │
│       ┌───────────────┐                             │
│       │  Audit MCP    │                             │
│       │  Port: 3001   │                             │
│       └───────────────┘                             │
│                                                     │
│  ┌────────────────────────────────┐                 │
│  │      Email Sending             │                 │
│  └────────────┬───────────────────┘                 │
│               │                                     │
│               ▼                                     │
│       ┌───────────────┐                             │
│       │  Email MCP    │                             │
│       │  Port: 3003   │                             │
│       └───────────────┘                             │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Use Cases

### 1. Post to Social Media from Any App

```javascript
// From any application
fetch('http://localhost:3000/post-all', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "Product launch announcement!",
    image_path: "/path/to/image.png"
  })
});
```

### 2. Generate CEO Briefing Programmatically

```python
# From any Python script
import requests

response = requests.post('http://localhost:3001/generate_briefing')
briefing = response.json()
print(briefing['path'])
```

### 3. Check Messages from Dashboard

```javascript
// From web dashboard
fetch('http://localhost:3002/inbox')
  .then(r => r.json())
  .then(data => console.log(`You have ${data.count} messages`));
```

---

## 🔐 Security Notes

**Current Implementation:**
- ✅ Localhost only (no external access)
- ✅ No authentication (trusted network)

**For Production:**
- Add API key authentication
- Enable HTTPS
- Add rate limiting
- Configure CORS properly

---

## 📝 Troubleshooting

### Port already in use

```bash
# Windows - Find and kill process
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Node.js dependencies missing

```bash
cd mcp_servers
npm install
```

### Python import errors

```bash
cd phase3_gold
py -m pip install playwright python-dotenv
```

---

## ✅ Testing Checklist

- [ ] Social MCP starts on port 3000
- [ ] Audit MCP starts on port 3001
- [ ] Communication MCP starts on port 3002
- [ ] All /health endpoints respond
- [ ] Can post to Facebook via API
- [ ] Can post to Instagram via API
- [ ] Can post to Twitter via API
- [ ] Can generate CEO briefing via API
- [ ] Can check inbox via API

---

**Version:** Gold Tier 1.0  
**Last Updated:** 2026-03-01  
**Status:** ✅ Complete
