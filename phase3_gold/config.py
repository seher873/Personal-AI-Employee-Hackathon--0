"""
Configuration loader - Loads credentials from .env file
All auto posting scripts import credentials from this module.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# Facebook Credentials
# =============================================================================
FB_EMAIL = os.getenv("FB_EMAIL", "")
FB_PASSWORD = os.getenv("FB_PASSWORD", "")

# =============================================================================
# Instagram Credentials
# =============================================================================
IG_USERNAME = os.getenv("IG_USERNAME", "")
IG_PASSWORD = os.getenv("IG_PASSWORD", "")

# =============================================================================
# Twitter/X Credentials
# =============================================================================
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")

# =============================================================================
# Gmail Credentials
# =============================================================================
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")

# =============================================================================
# MCP Server Configuration
# =============================================================================
MCP_PORT = int(os.getenv("MCP_PORT", "3000"))
AUDIT_MCP_PORT = int(os.getenv("AUDIT_MCP_PORT", "3001"))

# =============================================================================
# Post Content Configuration
# =============================================================================
POST_TEXT = "Hello from AI Employee! 🤖 #AI #Automation"
# Use absolute path for image
import os as _os
IMAGE_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "post_image.png")


def validate_credentials():
    """Validate that all required credentials are set."""
    issues = []
    
    if not FB_EMAIL or FB_EMAIL == "your_facebook_email@example.com":
        issues.append("FB_EMAIL not set in .env")
    if not FB_PASSWORD or FB_PASSWORD == "your_facebook_password":
        issues.append("FB_PASSWORD not set in .env")
    
    if not IG_USERNAME or IG_USERNAME == "your_instagram_username":
        issues.append("IG_USERNAME not set in .env")
    if not IG_PASSWORD or IG_PASSWORD == "your_instagram_password":
        issues.append("IG_PASSWORD not set in .env")
    
    if not TWITTER_EMAIL or TWITTER_EMAIL == "your_email@example.com":
        issues.append("TWITTER_EMAIL not set in .env")
    if not TWITTER_PASSWORD or TWITTER_PASSWORD == "your_password":
        issues.append("TWITTER_PASSWORD not set in .env")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


def print_config_status():
    """Print status of loaded credentials (without showing actual values)."""
    print("=" * 60)
    print("Configuration Status")
    print("=" * 60)
    
    status = validate_credentials()
    if status["valid"]:
        print("✅ All credentials loaded successfully")
    else:
        print("⚠️ Missing credentials:")
        for issue in status["issues"]:
            print(f"   - {issue}")
    
    print(f"Facebook Email: {'***' if FB_EMAIL else 'Not set'}")
    print(f"Instagram Username: {'***' if IG_USERNAME else 'Not set'}")
    print(f"Twitter Email: {'***' if TWITTER_EMAIL else 'Not set'}")
    print(f"Gmail Email: {'***' if GMAIL_EMAIL else 'Not set'}")
    print(f"MCP Port: {MCP_PORT}")
    print(f"Audit MCP Port: {AUDIT_MCP_PORT}")
    print("=" * 60)
