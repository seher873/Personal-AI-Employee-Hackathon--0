# Invoice Automation Workflow
## Complete Scenario: WhatsApp → Invoice → Email → Log

---

## 📋 Scenario

A client sends a WhatsApp message asking for an invoice. The AI Employee automatically:

1. ✅ Detects the request
2. ✅ Generates the invoice
3. ✅ Sends it via email
4. ✅ Logs the transaction

---

## 🚀 Quick Start

### Test the Complete Workflow:

```powershell
cd C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold

# Run complete workflow test
py Skills\skill_invoice_workflow.py
```

---

## 📊 Workflow Steps

### Step 1: Detection (WhatsApp Watcher)

The WhatsApp Watcher detects a message containing the keyword "invoice":

```python
# Detected message:
# From: Client A
# Text: "Hey, can you send me the invoice for January?"

# Watcher creates:
# /Vault/Needs_Action/WHATSAPP_client_a_2026-01-07.md
```

**Keywords detected:**
- invoice
- billing
- bill
- payment
- receipt
- "send invoice"
- "send me invoice"

---

### Step 2: Generate Invoice

```python
from Skills.skill_invoice_generator import InvoiceGenerator

generator = InvoiceGenerator()

result = generator.generate_invoice(
    client_name="Client A",
    client_email="client@example.com",
    description="AI Services - January 2026",
    amount=500.00
)

# Output:
# Invoice Number: INV-20260107123456
# File: ./Invoices/INV-20260107123456_Client_A.md
# Total: $500.00
```

**Invoice includes:**
- Invoice number (auto-generated)
- Client details
- Service description
- Amount with tax calculation
- Payment terms
- Bank details

---

### Step 3: Send via Email

```python
from Skills.skill_send_invoice_email import InvoiceEmailSender

sender = InvoiceEmailSender()

result = sender.send_invoice_email(
    client_email="client@example.com",
    invoice_number="INV-20260107123456",
    invoice_path="./Invoices/INV-20260107123456_Client_A.md",
    amount=500.00
)

# Output:
# Email sent successfully!
```

**Email includes:**
- Professional email template
- Invoice content
- Payment instructions
- Contact information

---

### Step 4: Log Transaction

```json
{
  "timestamp": "2026-01-07T12:34:56",
  "type": "invoice_workflow",
  "client_name": "Client A",
  "invoice_number": "INV-20260107123456",
  "amount": 500.00,
  "email_sent": true,
  "status": "completed"
}
```

**Logged to:**
- `./Logs/invoice_transactions.jsonl`
- `./Logs/invoice_workflow.log`

---

## 🔄 Complete Workflow Example

```python
from Skills.skill_invoice_workflow import InvoiceWorkflowOrchestrator

orchestrator = InvoiceWorkflowOrchestrator()

# Process WhatsApp invoice request
result = orchestrator.process_whatsapp_invoice_request(
    client_name="Client A",
    message="Hey, can you send me the invoice for January?"
)

# Result:
{
  "success": True,
  "client_name": "Client A",
  "steps": {
    "detection": "invoice_request_detected",
    "invoice_generation": {
      "success": True,
      "invoice_number": "INV-20260107123456",
      "amount": 500.00
    },
    "email_sent": {
      "success": True,
      "client_email": "client@example.com"
    },
    "transaction_logged": True
  }
}
```

---

## 📁 File Structure

```
phase3_gold/
├── Skills/
│   ├── skill_invoice_generator.py      # Generate invoices
│   ├── skill_whatsapp_invoice.py       # Detect invoice requests
│   ├── skill_send_invoice_email.py     # Send invoice emails
│   └── skill_invoice_workflow.py       # Complete orchestrator
│
├── Invoices/                           # Generated invoices
│   ├── INV-20260107123456_Client_A.md
│   └── INV-20260107123456_metadata.json
│
├── Logs/
│   ├── invoice_workflow.log           # Workflow logs
│   ├── invoice_transactions.jsonl     # Transaction log
│   └── invoice_handler.log            # Detection logs
│
└── Needs_Action/                       # Action files
    └── WHATSAPP_client_a_20260107.md
```

---

## 🎯 Customization

### Change Invoice Amounts

Edit `skill_whatsapp_invoice.py`:

```python
self.default_amounts = {
    'january': 500,
    'february': 750,
    'march': 1000,
    'default': 500
}
```

### Change Invoice Template

Edit `skill_invoice_generator.py`:

```python
self.template = {
    "company_name": "Your Company",
    "company_address": "Your Address",
    "currency": "USD",
    "tax_rate": 0.15  # 15%
}
```

### Add More Keywords

Edit `skill_whatsapp_invoice.py`:

```python
self.invoice_keywords = [
    'invoice', 'billing', 'bill', 'payment', 
    'receipt', 'send invoice', 'send me invoice'
    # Add more:
    'please bill me', 'charge me', 'monthly invoice'
]
```

---

## 🔧 Process Management (Keep Running 24/7)

### Using PM2 (Recommended):

```bash
# Install PM2
npm install -g pm2

# Start all services
cd C:\Users\user\Desktop\AI_Employee_Vault\phase3_gold
pm2 start ecosystem.config.json

# Save process list
pm2 save

# Start on reboot
pm2 startup
```

### PM2 Commands:

```bash
# View status
pm2 status

# View logs
pm2 logs

# Restart all
pm2 restart all

# Stop all
pm2 stop all
```

---

## 📊 Monitoring

### View Transaction Logs:

```powershell
# View latest transactions
Get-Content Logs\invoice_transactions.jsonl -Tail 10

# View workflow logs
Get-Content Logs\invoice_workflow.log -Tail 20
```

### Check Invoice Files:

```powershell
# List all invoices
dir Invoices\*.md

# View invoice
notepad Invoices\INV-20260107123456_Client_A.md
```

---

## ✅ Testing Checklist

- [ ] Run workflow test: `py Skills\skill_invoice_workflow.py`
- [ ] Check invoice generated in `Invoices/`
- [ ] Check email sent (or pending)
- [ ] Check transaction logged in `Logs/`
- [ ] Test with different months
- [ ] Test with custom amounts
- [ ] Test with different keywords

---

## 🚨 Troubleshooting

### Invoice Not Generated
- Check `.env` has Gmail credentials
- Check `Invoices/` folder permissions

### Email Not Sent
- Check Email MCP Server running: `http://localhost:3003/health`
- Check Gmail App Password is valid
- Check `Pending_Emails/` for queued emails

### Keywords Not Detected
- Add more keywords to `invoice_keywords` list
- Check message text is lowercase

---

**Version:** Gold Tier 1.0  
**Last Updated:** 2026-03-02  
**Status:** ✅ Complete Workflow
