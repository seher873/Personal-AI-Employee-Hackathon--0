"""
AI Orchestrator - Routes and processes incoming messages from watchers
Handles domain classification, task routing, and coordination with MCP servers.
"""

import os
import time
import json
import datetime
import glob
from pathlib import Path
from config import validate_credentials

# =============================================================================
# CONFIGURATION
# =============================================================================
INBOX_DIR = "./Inbox"
NEEDS_ACTION_DIR = "./Needs_Action"
DONE_DIR = "./Done"
SKILL_FILE = "./SKILL.md"

# Create directories if they don't exist
os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
os.makedirs(DONE_DIR, exist_ok=True)


def classify_domain(source):
    """Classify message domain based on source."""
    personal_domains = ["gmail", "whatsapp"]
    business_domains = ["linkedin", "facebook", "instagram", "twitter"]
    
    if source in personal_domains:
        return "personal"
    elif source in business_domains:
        return "business"
    else:
        return "unknown"


def route_to_handler(message_data):
    """Route message to appropriate handler based on domain and content."""
    domain = classify_domain(message_data.get("source", "unknown"))
    
    # Extract key information
    title = message_data.get("title", "")
    description = message_data.get("description", "")
    content = message_data.get("content", "")
    
    # Simple intent detection
    if any(keyword in title.lower() or keyword in description.lower() for keyword in ["post", "share", "tweet", "instagram", "facebook", "linkedin"]):
        return f"social_post_handler({domain})"
    elif any(keyword in title.lower() or keyword in description.lower() for keyword in ["email", "message", "chat"]):
        return f"message_handler({domain})"
    elif any(keyword in title.lower() or keyword in description.lower() for keyword in ["task", "todo", "action"]):
        return f"task_handler({domain})"
    else:
        return f"default_handler({domain})"


def process_inbox():
    """Process all files in the Inbox directory."""
    print("Processing Inbox...")
    
    # Get all markdown files in Inbox
    inbox_files = glob.glob(os.path.join(INBOX_DIR, "*.md"))
    
    if not inbox_files:
        print("No messages in Inbox")
        return
    
    for filepath in inbox_files:
        try:
            print(f"Processing: {os.path.basename(filepath)}")
            
            # Read the file
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Parse YAML front matter and content
            lines = content.split('\n')
            front_matter = {}
            content_lines = []
            in_front_matter = False
            
            for line in lines:
                if line.strip() == "---":
                    if not in_front_matter:
                        in_front_matter = True
                    else:
                        break
                elif in_front_matter:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        front_matter[key.strip()] = value.strip().strip('"').strip("'")
                else:
                    content_lines.append(line)
            
            # Extract message data
            message_data = {
                "source": front_matter.get("source", "unknown"),
                "status": front_matter.get("status", "pending"),
                "created": front_matter.get("created", datetime.datetime.now().isoformat()),
                "title": "",
                "description": "",
                "content": "\n".join(content_lines).strip()
            }
            
            # Parse title and description from content
            content_text = message_data["content"]
            if content_text.startswith("#"):
                title_end = content_text.find("\n")
                if title_end > 0:
                    message_data["title"] = content_text[1:title_end].strip()
                    message_data["description"] = content_text[title_end+1:].strip()
                else:
                    message_data["title"] = content_text[1:].strip()
            
            # Classify domain
            domain = classify_domain(message_data["source"])
            print(f"Domain: {domain}")
            
            # Route to handler
            handler = route_to_handler(message_data)
            print(f"Routing to: {handler}")
            
            # For now, just move to Needs_Action (simulating orchestration)
            filename = os.path.basename(filepath)
            new_path = os.path.join(NEEDS_ACTION_DIR, filename)
            
            # Update status in file
            with open(filepath, 'r') as f:
                file_content = f.read()
            
            # Replace status
            updated_content = file_content.replace("status: pending", "status: needs_action")
            
            # Write to Needs_Action
            with open(new_path, 'w') as f:
                f.write(updated_content)
            
            # Remove from Inbox
            os.remove(filepath)
            
            print(f"Moved to Needs_Action: {filename}")
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            # Move to Done with error status
            try:
                filename = os.path.basename(filepath)
                new_path = os.path.join(DONE_DIR, f"ERROR_{filename}")
                with open(filepath, 'r') as f:
                    content = f.read()
                with open(new_path, 'w') as f:
                    f.write(f"---\nstatus: error\nerror: {e}\n---\n{content}")
                os.remove(filepath)
            except:
                pass


def check_needs_action():
    """Check for items that need action."""
    print("Checking Needs_Action directory...")
    
    needs_action_files = glob.glob(os.path.join(NEEDS_ACTION_DIR, "*.md"))
    
    if not needs_action_files:
        print("No items needing action")
        return
    
    for filepath in needs_action_files:
        try:
            print(f"Processing needs action: {os.path.basename(filepath)}")
            
            # For demo purposes, just move to Done after "processing"
            filename = os.path.basename(filepath)
            new_path = os.path.join(DONE_DIR, filename)
            
            # Update status to completed
            with open(filepath, 'r') as f:
                content = f.read()
            
            updated_content = content.replace("status: needs_action", "status: completed")
            
            with open(new_path, 'w') as f:
                f.write(updated_content)
            
            os.remove(filepath)
            print(f"Completed: {filename}")
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def main():
    """Main orchestrator function."""
    print("=" * 60)
    print("AI Orchestrator - Message Routing and Processing")
    print("=" * 60)
    
    # Validate credentials
    config_status = validate_credentials()
    if not config_status["valid"]:
        print("⚠️  Missing credentials detected:")
        for issue in config_status["issues"]:
            print(f"   - {issue}")
    
    print("Starting orchestrator...")
    
    try:
        while True:
            print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Checking for new messages...")
            
            # Process Inbox
            process_inbox()
            
            # Check Needs_Action
            check_needs_action()
            
            # Wait before next check
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n\nOrchestrator stopped by user")
    except Exception as e:
        print(f"\nOrchestrator error: {e}")
        raise


if __name__ == "__main__":
    main()