"""
Configuration loader - Loads credentials from .env file
All auto posting scripts import credentials from this module.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (override existing)
load_dotenv(override=True)

# =============================================================================
# Facebook Credentials
# =============================================================================
FB_EMAIL = os.getenv("FB_EMAIL", "")
FB_PASSWORD = os.getenv("FB_PASSWORD", "")

# Facebook API Credentials
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "")

# =============================================================================
# Instagram Credentials
# =============================================================================
IG_USERNAME = os.getenv("IG_USERNAME", "")
IG_PASSWORD = os.getenv("IG_PASSWORD", "")

# Instagram API Credentials
IG_ID = os.getenv("IG_ID", "")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "")

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
# Twitter/X Credentials
# =============================================================================
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# =============================================================================
# WhatsApp Credentials
# =============================================================================
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "")
WHATSAPP_BUSINESS_ID = os.getenv("WHATSAPP_BUSINESS_ID", "")

# =============================================================================
# LinkedIn Credentials
# =============================================================================
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
COMPANY_URN = os.getenv("COMPANY_URN", "")

# =============================================================================
# MCP Server Configuration
# =============================================================================
MCP_PORT = int(os.getenv("MCP_PORT", "3000"))
AUDIT_MCP_PORT = int(os.getenv("AUDIT_MCP_PORT", "3001"))

# =============================================================================
# Post Content Configuration
# =============================================================================
POST_TEXT = "Hello from AI Employee! #AI #Automation"
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

    # LinkedIn credentials
    if not LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_ID == "your_linkedin_client_id":
        issues.append("LINKEDIN_CLIENT_ID not set in .env")
    if not LINKEDIN_ACCESS_TOKEN:
        issues.append("LINKEDIN_ACCESS_TOKEN not set in .env")

    # API credentials are optional (can use browser automation as fallback)
    api_issues = []
    if not FB_ACCESS_TOKEN:
        api_issues.append("FB_ACCESS_TOKEN not set (optional, browser fallback available)")
    if not FB_PAGE_ID:
        api_issues.append("FB_PAGE_ID not set (optional, browser fallback available)")
    if not IG_ID:
        api_issues.append("IG_ID not set (optional, browser fallback available)")
    if not IG_ACCESS_TOKEN:
        api_issues.append("IG_ACCESS_TOKEN not set (optional, browser fallback available)")
    if not LINKEDIN_CLIENT_SECRET:
        api_issues.append("LINKEDIN_CLIENT_SECRET not set (optional)")
    if not COMPANY_URN:
        api_issues.append("COMPANY_URN not set (optional)")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "api_issues": api_issues
    }


def print_config_status():
    """Print status of loaded credentials (without showing actual values)."""
    import sys
    # Handle Windows console encoding
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("Configuration Status")
    print("=" * 60)

    status = validate_credentials()
    if status["valid"]:
        print("[OK] All credentials loaded successfully")
    else:
        print("[WARN] Missing credentials:")
        for issue in status["issues"]:
            print(f"   - {issue}")

    print(f"Facebook Email: {'***' if FB_EMAIL else 'Not set'}")
    print(f"Facebook Page ID: {'***' if FB_PAGE_ID else 'Not set'}")
    print(f"Facebook Token: {'***' if FB_ACCESS_TOKEN else 'Not set'}")
    print(f"Instagram Username: {'***' if IG_USERNAME else 'Not set'}")
    print(f"Instagram ID: {'***' if IG_ID else 'Not set'}")
    print(f"Instagram Token: {'***' if IG_ACCESS_TOKEN else 'Not set'}")
    print(f"Twitter Email: {'***' if TWITTER_EMAIL else 'Not set'}")
    print(f"Gmail Email: {'***' if GMAIL_EMAIL else 'Not set'}")
    print(f"WhatsApp Phone: {'***' if WHATSAPP_PHONE else 'Not set'}")
    print(f"LinkedIn Client ID: {'***' if LINKEDIN_CLIENT_ID else 'Not set'}")
    print(f"LinkedIn Token: {'***' if LINKEDIN_ACCESS_TOKEN else 'Not set'}")
    print(f"Company URN: {'***' if COMPANY_URN else 'Not set'}")
    print(f"MCP Port: {MCP_PORT}")
    print(f"Audit MCP Port: {AUDIT_MCP_PORT}")
    print("=" * 60)
