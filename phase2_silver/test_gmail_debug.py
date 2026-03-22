#!/usr/bin/env python3
"""Debug Gmail IMAP connection"""
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone

load_dotenv()

email_address = os.getenv('GMAIL_ADDRESS')
app_password = os.getenv('GMAIL_APP_PASSWORD')

print(f"Connecting as: {email_address}")

# Connect to Gmail
imap = imaplib.IMAP4_SSL('imap.gmail.com')
imap.login(email_address, app_password)
imap.select('INBOX')

# Search ALL emails
status, messages = imap.search(None, 'ALL')
email_ids = messages[0].split()

print(f"\nTotal emails in inbox: {len(email_ids)}")
print(f"\nLast 5 emails:")

for email_id in email_ids[-5:]:
    status, msg_data = imap.fetch(email_id, '(RFC822)')
    msg = email.message_from_bytes(msg_data[0][1])
    
    subject = decode_header(msg.get('Subject', ''))
    subject_str = ''
    for fragment, encoding in subject:
        if isinstance(fragment, bytes):
            subject_str += fragment.decode(encoding or 'utf-8', errors='ignore')
        else:
            subject_str += fragment
    
    date_str = msg.get('Date', '')
    try:
        email_time = email.utils.parsedate_to_datetime(date_str)
        print(f"  ID: {email_id}, Date: {email_time}, Subject: {subject_str}")
    except Exception as e:
        print(f"  ID: {email_id}, Date: {date_str}, Subject: {subject_str} [parse error: {e}]")

# Check UNSEEN emails
status, unseen = imap.search(None, 'UNSEEN')
unseen_ids = unseen[0].split() if unseen[0] else []
print(f"\nUnseen emails: {len(unseen_ids)}")

imap.close()
imap.logout()
print("\nDone!")
