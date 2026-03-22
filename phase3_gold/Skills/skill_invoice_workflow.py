#!/usr/bin/env python3
"""
Invoice Workflow Orchestrator
Gold Tier - Complete automation: WhatsApp → Invoice → Email → Log

Workflow:
1. WhatsApp detects "invoice" keyword
2. Generate invoice automatically
3. Send invoice via email
4. Log transaction
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Skills.skill_whatsapp_invoice import WhatsAppInvoiceHandler
from Skills.skill_send_invoice_email import InvoiceEmailSender


class InvoiceWorkflowOrchestrator:
    """Orchestrate complete invoice workflow"""
    
    def __init__(self):
        self.invoice_handler = WhatsAppInvoiceHandler()
        self.email_sender = InvoiceEmailSender()
        
        self.logs_dir = Path(__file__).parent.parent / "Logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.log("Invoice Workflow Orchestrator initialized")
    
    def log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        log_file = self.logs_dir / "invoice_workflow.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def process_whatsapp_invoice_request(self, client_name: str, message: str) -> dict:
        """
        Complete workflow: WhatsApp invoice request → Email invoice
        
        Args:
            client_name: Client name from WhatsApp
            message: WhatsApp message text
        
        Returns:
            dict: Complete workflow result
        """
        self.log("=" * 60)
        self.log("INVOICE WORKFLOW STARTED")
        self.log(f"Client: {client_name}")
        self.log(f"Message: {message}")
        self.log("=" * 60)
        
        workflow_result = {
            "client_name": client_name,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "steps": {}
        }
        
        # Step 1: Check if it's an invoice request
        self.log("\n[Step 1/4] Checking if invoice request...")
        if not self.invoice_handler.is_invoice_request(message):
            self.log("Not an invoice request - skipping")
            workflow_result["steps"]["detection"] = "not_invoice_request"
            workflow_result["success"] = False
            return workflow_result
        
        self.log("✓ Invoice request detected")
        workflow_result["steps"]["detection"] = "invoice_request_detected"
        
        # Step 2: Generate invoice
        self.log("\n[Step 2/4] Generating invoice...")
        invoice_result = self.invoice_handler.process_invoice_request(
            client_name=client_name,
            message=message
        )
        
        if not invoice_result.get('success'):
            self.log(f"✗ Invoice generation failed: {invoice_result.get('error')}")
            workflow_result["steps"]["invoice_generation"] = "failed"
            workflow_result["success"] = False
            return workflow_result
        
        self.log(f"✓ Invoice generated: {invoice_result['invoice_number']}")
        self.log(f"  Amount: ${invoice_result['total']:,.2f}")
        self.log(f"  File: {invoice_result['file_path']}")
        workflow_result["steps"]["invoice_generation"] = {
            "success": True,
            "invoice_number": invoice_result['invoice_number'],
            "amount": invoice_result['total'],
            "file_path": invoice_result['file_path']
        }
        
        # Step 3: Send email
        self.log("\n[Step 3/4] Sending invoice via email...")
        email_result = self.email_sender.send_invoice_email(
            client_email=invoice_result['client_email'],
            invoice_number=invoice_result['invoice_number'],
            invoice_path=invoice_result['file_path'],
            amount=invoice_result['total']
        )
        
        if email_result.get('success'):
            self.log(f"✓ Email sent to {invoice_result['client_email']}")
            workflow_result["steps"]["email_sent"] = {
                "success": True,
                "client_email": invoice_result['client_email']
            }
        else:
            self.log(f"⚠ Email send failed: {email_result.get('error')}")
            workflow_result["steps"]["email_sent"] = {
                "success": False,
                "error": email_result.get('error')
            }
        
        # Step 4: Log transaction
        self.log("\n[Step 4/4] Logging transaction...")
        self.log_transaction(workflow_result)
        self.log("✓ Transaction logged")
        workflow_result["steps"]["transaction_logged"] = True
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log("INVOICE WORKFLOW COMPLETED")
        self.log("=" * 60)
        self.log(f"Client: {client_name}")
        self.log(f"Invoice: {invoice_result['invoice_number']}")
        self.log(f"Amount: ${invoice_result['total']:,.2f}")
        self.log(f"Email: {email_result.get('success', False)}")
        self.log("=" * 60)
        
        workflow_result["success"] = True
        return workflow_result
    
    def log_transaction(self, workflow_result: dict):
        """Log complete transaction"""
        transaction = {
            "timestamp": datetime.now().isoformat(),
            "type": "invoice_workflow",
            "client_name": workflow_result['client_name'],
            "invoice_number": workflow_result['steps'].get('invoice_generation', {}).get('invoice_number'),
            "amount": workflow_result['steps'].get('invoice_generation', {}).get('amount'),
            "email_sent": workflow_result['steps'].get('email_sent', {}).get('success', False),
            "status": "completed" if workflow_result.get('success') else "failed"
        }
        
        # Save to transactions log
        transactions_file = self.logs_dir / "invoice_transactions.jsonl"
        with open(transactions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(transaction) + "\n")
        
        # Also save full workflow log
        workflow_file = self.logs_dir / f"workflow_{workflow_result['client_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_result, f, indent=2)


if __name__ == '__main__':
    # Test complete workflow
    orchestrator = InvoiceWorkflowOrchestrator()
    
    # Test message
    test_message = "Hey, can you send me the invoice for January?"
    
    result = orchestrator.process_whatsapp_invoice_request(
        client_name="Test Client",
        message=test_message
    )
    
    print("\n" + "=" * 60)
    print("WORKFLOW RESULT")
    print("=" * 60)
    print(f"Success: {result.get('success', False)}")
    print(f"Client: {result.get('client_name')}")
    print(f"Steps completed: {len(result.get('steps', {}))}")
    print("=" * 60)
