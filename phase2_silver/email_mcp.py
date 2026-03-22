#!/usr/bin/env python3
"""
Email MCP Server
================
Model Context Protocol (MCP) server for sending emails via Gmail

Agent Skills:
- Send emails with attachments
- HTML and plain text support
- Multiple recipients (To, CC, BCC)
- Attachment handling
"""

import os
import sys
import smtplib
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "Logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'email_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EmailMCP')


class EmailMCP:
    """MCP Server for sending emails"""

    def __init__(self):
        self.address = GMAIL_ADDRESS
        self.password = GMAIL_APP_PASSWORD

    def send_email(self, to: str, subject: str, body: str, cc: str = None, 
                   bcc: str = None, html: bool = False, attachments: list = None) -> dict:
        """Send an email with optional attachments"""
        logger.info(f"Sending email to: {to}")
        
        if not self.address or not self.password:
            return {'success': False, 'message': 'Gmail credentials not set'}

        try:
            msg = MIMEMultipart()
            msg['From'] = self.address
            msg['To'] = to
            msg['Subject'] = subject
            if cc:
                msg['Cc'] = cc

            msg_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, msg_type))

            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 
                                       f'attachment; filename={os.path.basename(file_path)}')
                        msg.attach(part)

            recipients = [to]
            if cc:
                recipients.extend(cc.split(','))
            if bcc:
                recipients.extend(bcc.split(','))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(self.address, self.password)
            server.sendmail(self.address, recipients, msg.as_string())
            server.quit()

            logger.info(f"Email sent successfully to {to}")
            return {'success': True, 'message': f'Email sent to {to}'}

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {'success': False, 'message': str(e)}

    def send_notification(self, to: str, title: str, message: str) -> dict:
        """Send a notification email"""
        subject = f"🔔 {title}"
        body = f"Notification from AI Employee Vault\n\n{message}\n\n---\nAutomated message"
        return self.send_email(to, subject, body)

    def send_report(self, to: str, report_type: str, content: str, 
                    attachments: list = None) -> dict:
        """Send a report email"""
        subject = f"📊 {report_type} Report"
        body = f"{report_type} Report\n\n{content}\n\n---\nAI Employee Vault"
        return self.send_email(to, subject, body, attachments=attachments)


def main():
    """Main entry point"""
    print("=" * 60)
    print("📧 Email MCP Server - Silver Tier")
    print("=" * 60)
    print(f"\nGmail: {GMAIL_ADDRESS if GMAIL_ADDRESS else 'Not configured'}")
    print("\nAvailable Actions:")
    print("  - send_email")
    print("  - send_notification")
    print("  - send_report")
    print("=" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        if GMAIL_ADDRESS:
            print(f"\n🧪 Sending test email to: {GMAIL_ADDRESS}")
            mcp = EmailMCP()
            result = mcp.send_notification(
                GMAIL_ADDRESS,
                "MCP Server Test",
                "Email MCP Server is working!"
            )
            print(f"Result: {result}")
        else:
            print("\n❌ GMAIL_ADDRESS not set in .env")


if __name__ == '__main__':
    main()
