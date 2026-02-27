"""
Selector Loader - Dynamic Selector Management
Loads selectors from selectors.json and provides helper functions.
No code changes needed when website selectors change - just update selectors.json
"""

import os
import json
from typing import List, Optional, Dict, Any

SELECTORS_FILE = os.path.join(os.path.dirname(__file__), "selectors.json")

# Cache loaded selectors
_selectors_cache: Optional[Dict[str, Any]] = None


def load_selectors() -> Dict[str, Any]:
    """Load selectors from JSON file."""
    global _selectors_cache
    
    if _selectors_cache is not None:
        return _selectors_cache
    
    if not os.path.exists(SELECTORS_FILE):
        raise FileNotFoundError(f"Selectors file not found: {SELECTORS_FILE}")
    
    with open(SELECTORS_FILE, 'r') as f:
        _selectors_cache = json.load(f)
    
    return _selectors_cache


def reload_selectors() -> Dict[str, Any]:
    """Force reload selectors from file."""
    global _selectors_cache
    _selectors_cache = None
    return load_selectors()


def get_selector(platform: str, key: str, default: str = "") -> str:
    """Get a single selector string for a platform."""
    selectors = load_selectors()
    return selectors.get(platform, {}).get(key, default)


def get_selector_list(platform: str, key: str) -> List[str]:
    """Get a list of selectors for a platform (for fallback)."""
    selectors = load_selectors()
    value = selectors.get(platform, {}).get(key, [])
    if isinstance(value, str):
        return [value]
    return value


def get_timeout(key: str, default: int = 30000) -> int:
    """Get timeout value."""
    selectors = load_selectors()
    return selectors.get("timeouts", {}).get(key, default)


def get_delay(key: str, default: int = 1000) -> int:
    """Get delay value in milliseconds."""
    selectors = load_selectors()
    return selectors.get("delays", {}).get(key, default)


def build_locator_query(selectors: List[str], locator_type: str = "button") -> str:
    """Build a Playwright locator query from multiple selectors."""
    if not selectors:
        return ""
    
    if locator_type == "button":
        parts = []
        for sel in selectors:
            parts.append(f'button:has-text("{sel}")')
            parts.append(f'div[role="button"]:has-text("{sel}")')
            parts.append(f'span[role="button"]:has-text("{sel}")')
        return ", ".join(parts)
    
    return ", ".join(selectors)


def validate_selectors() -> Dict[str, Any]:
    """Validate selectors file structure."""
    required_platforms = ["twitter", "facebook", "instagram"]
    required_timeouts = ["page_load", "selector_wait", "button_wait", "feed_wait", "post_wait"]
    required_delays = ["human_min", "human_max", "after_login", "after_post"]
    
    selectors = load_selectors()
    issues = []
    warnings = []
    
    # Check platforms
    for platform in required_platforms:
        if platform not in selectors:
            issues.append(f"Missing platform: {platform}")
    
    # Check timeouts
    for timeout_key in required_timeouts:
        if timeout_key not in selectors.get("timeouts", {}):
            warnings.append(f"Missing timeout: {timeout_key}")
    
    # Check delays
    for delay_key in required_delays:
        if delay_key not in selectors.get("delays", {}):
            warnings.append(f"Missing delay: {delay_key}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }


def update_selector(platform: str, key: str, value: str) -> bool:
    """Update a selector in the JSON file."""
    try:
        selectors = load_selectors()
        
        if platform not in selectors:
            selectors[platform] = {}
        
        selectors[platform][key] = value
        
        with open(SELECTORS_FILE, 'w') as f:
            json.dump(selectors, f, indent=2)
        
        # Clear cache
        global _selectors_cache
        _selectors_cache = None
        
        return True
    except Exception as e:
        print(f"Error updating selector: {e}")
        return False


def get_all_selectors() -> Dict[str, Any]:
    """Get all selectors."""
    return load_selectors()


def print_selectors_summary():
    """Print a summary of loaded selectors."""
    selectors = load_selectors()
    
    print("=" * 60)
    print("LOADED SELECTORS")
    print("=" * 60)
    
    for platform in ["twitter", "facebook", "instagram"]:
        if platform in selectors:
            print(f"\n{platform.upper()}:")
            for key, value in selectors[platform].items():
                if isinstance(value, list):
                    print(f"  {key}: {', '.join(value)}")
                else:
                    print(f"  {key}: {value}")
    
    print("\nTIMEOUTS:")
    for key, value in selectors.get("timeouts", {}).items():
        print(f"  {key}: {value}ms")
    
    print("\nDELAYS:")
    for key, value in selectors.get("delays", {}).items():
        print(f"  {key}: {value}ms")
    
    print("=" * 60)


if __name__ == "__main__":
    print_selectors_summary()
    
    print("\nVALIDATION:")
    result = validate_selectors()
    if result["valid"]:
        print("✅ Selectors file is valid")
    else:
        print("❌ Issues found:")
        for issue in result["issues"]:
            print(f"  - {issue}")
    
    if result["warnings"]:
        print("⚠️ Warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
