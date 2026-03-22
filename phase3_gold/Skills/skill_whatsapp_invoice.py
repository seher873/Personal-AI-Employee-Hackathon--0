#!/usr/bin/env python3
"""
WhatsApp Invoice Request Handler
Gold Tier - Detect invoice requests and automate workflow

Workflow:
1. Detect "invoice" keyword in WhatsApp message
2. Generate invoice
3. Send via email
4. Log transaction
"""

import sys
import re
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Skills.skill_invoice_generator import InvoiceGenerator


class WhatsAppInvoiceHandler:
    """Handle invoice requests from WhatsApp"""
    
    def __init__(self):
        self.invoice_generator = InvoiceGenerator()
        self.logs_dir = Path(__file__).parent.parent / "Logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Invoice keywords
        self.invoice_keywords = [
            'invoice', 'billing', 'bill', 'payment', 'receipt', 
            'send invoice', 'send me invoice', 'can you send'
        ]
        
        # Default invoice amounts (can be customized)
        self.default_amounts = {
            'january': 500,
            'february': 500,
            'march': 500,
            'default': 500
        }
        
        self.log("WhatsApp Invoice Handler initialized")
    
    def log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        log_file = self.logs_dir / "invoice_handler.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def is_invoice_request(self, message: str) -> bool:
        """Check if message is an invoice request"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.invoice_keywords)
    
    def extract_month(self, message: str) -> str:
        """Extract month from message"""
        months = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        
        message_lower = message.lower()
        for month in months:
            if month in message_lower:
                return month.capitalize()
        
        return "Current"
    
    def extract_amount(self, message: str) -> float:
        """Extract amount from message if mentioned"""
        # Look for patterns like "$500", "500 dollars", "amount 500"
        patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|usd?)',
            r'amount[:\s]+(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                return float(amount_str)
        
        return None
    
    def get_client_email(self, client_name: str, message: str) -> str:
        """
        Get client email
        In production, this would lookup from CRM/database
        For now, extract from message or use placeholder
        """
        # Try to extract email from message
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, message)
        
        if match:
            return match.group()
        
        # Placeholder - in production, lookup from database
        return f"{client_name.lower().replace(' ', '.')}@example.com"
    
    def process_invoice_request(self, client_name: str, message: str) -> dict:
        """
        Process invoice request from WhatsApp
        
        Args:
            client_name: Client name from WhatsApp
            message: WhatsApp message text
        
        Returns:
            dict: Result with invoice details
        """
        self.log(f"Processing invoice request from {client_name}")
        self.log(f"Message: {message}")
        
        # Extract details
        month = self.extract_month(message)
        amount = self.extract_amount(message)
        
        if not amount:
            # Use default amount based on month
            month_key = month.lower()
            amount = self.default_amounts.get(month_key, self.default_amounts['default'])
        
        client_email = self.get_client_email(client_name, message)
        
        # Generate description
        description = f"AI Services - {month} 2026"
        
        self.log(f"Generating invoice for ${amount}")
        
        # Generate invoice
        result = self.invoice_generator.generate_invoice(
            client_name=client_name,
            client_email=client_email,
            description=description,
            amount=amount
        )
        
        if result['success']:
            self.log(f"Invoice generated: {result['invoice_number']}")
            
            # Log transaction
            self.log_transaction(client_name, client_email, result)
            
            return {
                "success": True,
                "invoice_number": result['invoice_number'],
                "total": result['total'],
                "file_path": result['file_path'],
                "client_email": client_email,
                "next_step": "send_email"
            }
        else:
            self.log("Invoice generation failed")
            return {"success": False, "error": "Invoice generation failed"}
    
    def log_transaction(self, client_name: str, client_email: str, invoice_result: dict):
        """Log transaction for audit"""
        transaction = {
            "timestamp": datetime.now().isoformat(),
            "type": "invoice_request",
            "source": "whatsapp",
            "client_name": client_name,
            "client_email": client_email,
            "invoice_number": invoice_result['invoice_number'],
            "amount": invoice_result['total'],
            "status": "generated"
        }
        
        # Save to transactions log
        transactions_file = self.logs_dir / "invoice_transactions.jsonl"
        with open(transactions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(transaction) + "\n")
        
        self.log(f"Transaction logged: {invoice_result['invoice_number']}")


if __name__ == '__main__':
    # Test invoice request handling
    handler = WhatsAppInvoiceHandler()
    
    # Test message
    test_message = "Hey, can you send me the invoice for January?"
    
    result = handler.process_invoice_request(
        client_name="Test Client",
        message=test_message
    )
    
    print("\n" + "=" * 60)
    print("INVOICE REQUEST PROCESSED")
    print("=" * 60)
    print(f"Client: Test Client")
    print(f"Message: {test_message}")
    print(f"Invoice Number: {result.get('invoice_number', 'N/A')}")
    print(f"Amount: ${result.get('total', 0):,.2f}")
    print(f"Status: {result.get('success', False)}")
    print("=" * 60)
