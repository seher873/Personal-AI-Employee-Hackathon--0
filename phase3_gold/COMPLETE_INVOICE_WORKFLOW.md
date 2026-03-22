# Complete Invoice Automation Workflow
## WhatsApp → Detection → Invoice → Email (with attachment) → Log

---

## 📋 Complete Scenario

```
Client sends WhatsApp: "Hey, can you send me the invoice for January?"
         ↓
1. WhatsApp Watcher detects "invoice" keyword
         ↓
2. Creates action file in Needs_Action/
         ↓
3. Orchestrator picks up the request
         ↓
4. Generates invoice (INV-20260302001234)
         ↓
5. Calls Email MCP Server with attachment
         ↓
6. Email sent with PDF invoice attached
         ↓
7. Transaction logged to /Vault/Logs/2026-03-02.json
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold\mcp_servers

# Install Node.js dependencies (includes nodemailer for emails)
npm install
```

### 2. Start Email MCP Server

```bash
# Start Email MCP
start_email_mcp.bat

# Or manually
node mcp_server_email.js
```

### 3. Test Complete Workflow

```bash
cd C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold
py Skills\skill_invoice_workflow.py
```

---

## 📊 Step-by-Step Implementation

### Step 1: WhatsApp Detection

```python
# WhatsApp Watcher detects invoice request
from Skills.skill_whatsapp_invoice import WhatsAppInvoiceHandler

handler = WhatsAppInvoiceHandler()

# Detected message
message = "Hey, can you send me the invoice for January?"
client_name = "Client A"

# Check if invoice request
if handler.is_invoice_request(message):
    print("✓ Invoice request detected")
```

**Keywords detected:**
- invoice, billing, bill, payment, receipt
- "send invoice", "send me invoice", "can you send"

---

### Step 2: Generate Invoice

```python
from Skills.skill_invoice_generator import InvoiceGenerator

generator = InvoiceGenerator()

result = generator.generate_invoice(
    client_name="Client A",
    client_email="client@example.com",
    description="AI Services - January 2026",
    amount=1500.00
)

# Output:
# Invoice Number: INV-20260302001234
# File: ./Invoices/INV-20260302001234_Client_A.md
# Total: $1,500.00
```

**Invoice saved to:** `./Invoices/INV-20260302001234_Client_A.md`

---

### Step 3: Email MCP Call (With Attachment)

```javascript
// MCP Call - Send email with invoice attachment
await fetch('http://localhost:3003/send-invoice', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    to: 'client_a@email.com',
    invoice_number: 'INV-20260302001234',
    invoice_path: 'C:/Vault/Invoices/INV-20260302001234_Client_A.md',
    amount: 1500,
    client_name: 'Client A'
  })
});

// Result:
{
  "success": true,
  "message": "Invoice sent successfully",
  "messageId": "<unique-message-id@gmail.com>",
  "timestamp": "2026-03-02T12:34:56.789Z"
}
```

---

### Step 4: Python Integration

```python
from Skills.skill_send_invoice_email import InvoiceEmailSender

sender = InvoiceEmailSender()

result = sender.send_invoice_email(
    client_email="client_a@email.com",
    invoice_number="INV-20260302001234",
    invoice_path="./Invoices/INV-20260302001234_Client_A.md",
    amount=1500.00
)

# Email MCP Server called automatically
# Email sent with attachment!
```

---

### Step 5: Transaction Logging

```json
// Logged to: ./Logs/2026-03-02.json
{
  "timestamp": "2026-03-02T12:34:56.789Z",
  "type": "invoice",
  "to": "client_a@email.com",
  "invoice_number": "INV-20260302001234",
  "amount": 1500,
  "invoice_path": "./Invoices/INV-20260302001234_Client_A.md",
  "messageId": "<unique-message-id@gmail.com>"
}
```

---

## 📧 Email MCP API Reference

### POST /send-email

Send a simple email:

```bash
curl -X POST http://localhost:3003/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "client@example.com",
    "subject": "Test Email",
    "body": "Hello from AI Employee!",
    "html": false,
    "attachment": "./path/to/file.pdf"
  }'
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| to | string | ✅ | Recipient email |
| subject | string | ✅ | Email subject |
| body | string | ✅ | Email body text |
| html | boolean | ❌ | Is HTML content |
| attachment | string | ❌ | File path to attach |

---

### POST /send-invoice

Send invoice with attachment (specialized):

```bash
curl -X POST http://localhost:3003/send-invoice \
  -H "Content-Type: application/json" \
  -d '{
    "to": "client@example.com",
    "invoice_number": "INV-20260302001234",
    "invoice_path": "./Invoices/INV-20260302001234.md",
    "amount": 1500,
    "client_name": "Client A"
  }'
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| to | string | ✅ | Client email |
| invoice_number | string | ✅ | Invoice number |
| invoice_path | string | ✅ | Path to invoice file |
| amount | number | ✅ | Invoice amount |
| client_name | string | ❌ | Client name |

---

### GET /health

Check server health:

```bash
curl http://localhost:3003/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "email-mcp-server",
  "port": 3003,
  "credentials_set": true,
  "uptime": 3600000,
  "stats": {
    "requests": 10,
    "emails_sent": 8,
    "emails_failed": 0,
    "invoices_sent": 5,
    "startTime": "2026-03-02T12:00:00.000Z"
  }
}
```

---

## 📁 File Structure

```
phase3_gold/
├── Skills/
│   ├── skill_invoice_generator.py
│   ├── skill_whatsapp_invoice.py
│   ├── skill_send_invoice_email.py
│   └── skill_invoice_workflow.py
│
├── mcp_servers/
│   ├── mcp_server_email.js        ← Email MCP with attachments
│   ├── mcp_server_social.js
│   ├── mcp_server_audit.py
│   └── mcp_server_communication.py
│
├── Invoices/                       ← Generated invoices
│   └── INV-20260302001234_Client_A.md
│
├── Logs/
│   ├── email_mcp_transactions.jsonl  ← All email transactions
│   ├── 2026-03-02.json              ← Daily log
│   └── invoice_workflow.log         ← Workflow logs
│
└── Needs_Action/                    ← Action files from watchers
    └── WHATSAPP_client_a_20260302.md
```

---

## 🔧 Configuration

### .env File

```ini
# Gmail Configuration
GMAIL_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_app_password  # NOT regular password!

# Get App Password from:
# https://myaccount.google.com/apppasswords
```

### Install Node.js Dependencies

```bash
cd mcp_servers
npm install
```

**Dependencies:**
- `express` - Web server
- `cors` - CORS support
- `nodemailer` - Email sending with attachments
- `dotenv` - Environment variables

---

## 🎯 Complete Code Example

```python
# Complete workflow from WhatsApp to Email
from Skills.skill_invoice_workflow import InvoiceWorkflowOrchestrator

orchestrator = InvoiceWorkflowOrchestrator()

# Process WhatsApp invoice request
result = orchestrator.process_whatsapp_invoice_request(
    client_name="Client A",
    message="Hey, can you send me the invoice for January?"
)

# Result:
print(f"Success: {result['success']}")
print(f"Invoice: {result['steps']['invoice_generation']['invoice_number']}")
print(f"Amount: ${result['steps']['invoice_generation']['amount']}")
print(f"Email Sent: {result['steps']['email_sent']['success']}")
```

---

## 📊 Transaction Logs

### View Email Transactions

```powershell
# View latest transactions
Get-Content Logs\email_mcp_transactions.jsonl -Tail 10

# View today's log
Get-Content Logs\2026-03-02.json
```

### Transaction Format

```json
{
  "timestamp": "2026-03-02T12:34:56.789Z",
  "type": "invoice",
  "to": "client_a@email.com",
  "invoice_number": "INV-20260302001234",
  "amount": 1500,
  "invoice_path": "./Invoices/INV-20260302001234_Client_A.md",
  "messageId": "<unique-message-id@gmail.com>"
}
```

---

## 🚨 Troubleshooting

### Email Not Sending

1. **Check Gmail credentials:**
   ```bash
   # In .env file
   GMAIL_EMAIL=your_email@gmail.com
   GMAIL_PASSWORD=your_app_password
   ```

2. **Check Email MCP is running:**
   ```bash
   curl http://localhost:3003/health
   ```

3. **Check Gmail App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Generate new app password
   - Update .env file

### Attachment Not Found

```
Error: Attachment not found: ./Invoices/INV-20260302001234.md
```

**Solution:**
- Check file path is correct
- Use absolute path: `C:/Users/.../Invoices/INV-20260302001234.md`
- Check file exists

### npm install Fails

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rmdir /s /q node_modules
npm install
```

---

## ✅ Testing Checklist

- [ ] Install dependencies: `npm install`
- [ ] Configure .env with Gmail credentials
- [ ] Start Email MCP: `node mcp_server_email.js`
- [ ] Test health: `curl http://localhost:3003/health`
- [ ] Send test email
- [ ] Send test invoice with attachment
- [ ] Check transaction logs
- [ ] Run complete workflow test

---

## 🎉 Success Indicators

```
✅ Email MCP Server running on port 3003
✅ Gmail credentials configured
✅ Invoice generated: INV-20260302001234
✅ Email sent with attachment
✅ Transaction logged to ./Logs/2026-03-02.json
✅ Client received invoice email
```

---

**Version:** Gold Tier 1.0  
**Last Updated:** 2026-03-02  
**Status:** ✅ Complete with Attachment Support
