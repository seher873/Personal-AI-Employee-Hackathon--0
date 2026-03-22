#!/usr/bin/env python3
"""
Email Sender - Send invoices via email
Gold Tier - Integration with Email MCP Server
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class InvoiceEmailSender:
    """Send invoices via email"""
    
    def __init__(self):
        self.mcp_email_url = "http://localhost:3003"
        self.logs_dir = Path(__file__).parent.parent / "Logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Email configuration
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        self.from_email = os.getenv("GMAIL_EMAIL", "")
        
        self.log("Invoice Email Sender initialized")
    
    def log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        log_file = self.logs_dir / "invoice_email.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def send_invoice_email(self, client_email: str, invoice_number: str, 
                          invoice_path: str, amount: float) -> dict:
        """
        Send invoice via email
        
        Args:
            client_email: Client email address
            invoice_number: Invoice number
            invoice_path: Path to invoice file
            amount: Invoice amount
        
        Returns:
            dict: Send result
        """
        self.log(f"Sending invoice {invoice_number} to {client_email}")
        
        # Read invoice content
        try:
            with open(invoice_path, 'r', encoding='utf-8') as f:
                invoice_content = f.read()
        except Exception as e:
            self.log(f"Error reading invoice: {e}")
            return {"success": False, "error": str(e)}
        
        # Create email body
        subject = f"Invoice {invoice_number} from AI Employee Services"
        
        body = f"""Dear Valued Client,

Please find your invoice attached.

Invoice Number: {invoice_number}
Amount: ${amount:,.2f}

Payment is due within 30 days of receipt.

If you have any questions, please don't hesitate to contact us.

Thank you for your business!

Best regards,
AI Employee Services
{self.from_email}

---

{invoice_content}
"""
        
        # Try to send via Email MCP Server
        try:
            response = requests.post(
                f"{self.mcp_email_url}/send-email",
                json={
                    "to": client_email,
                    "subject": subject,
                    "body": body,
                    "html": False
                },
                timeout=30
            )
            
            result = response.json()
            
            if result.get('success'):
                self.log(f"Email sent successfully to {client_email}")
                return {
                    "success": True,
                    "message": "Email sent",
                    "client_email": client_email
                }
            else:
                self.log(f"Email send failed: {result.get('error', 'Unknown error')}")
                return result
                
        except requests.exceptions.ConnectionError:
            self.log("Email MCP Server not available - saving to send later")
            # Save to pending emails
            self.save_pending_email(client_email, subject, body, invoice_number)
            return {
                "success": True,
                "message": "Email saved to pending (MCP server offline)",
                "pending": True
            }
        except Exception as e:
            self.log(f"Email send error: {e}")
            return {"success": False, "error": str(e)}
    
    def save_pending_email(self, to: str, subject: str, body: str, invoice_number: str):
        """Save email to pending queue"""
        pending_dir = self.logs_dir.parent / "Pending_Emails"
        pending_dir.mkdir(parents=True, exist_ok=True)
        
        email_data = {
            "to": to,
            "subject": subject,
            "body": body,
            "invoice_number": invoice_number,
            "created": datetime.now().isoformat(),
            "status": "pending"
        }
        
        filename = f"{invoice_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = pending_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(email_data, f, indent=2)
        
        self.log(f"Pending email saved: {filename}")


if __name__ == '__main__':
    # Test email sender
    sender = InvoiceEmailSender()
    
    result = sender.send_invoice_email(
        client_email="test@example.com",
        invoice_number="INV-TEST-001",
        invoice_path="test_invoice.md",
        amount=500.00
    )
    
    print(f"Result: {result}")
