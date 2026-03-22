"""
Imgur Image Uploader
Upload images to Imgur and get publicly accessible URLs for Instagram

Usage:
    from imgur_uploader import upload_to_imgur
    url = upload_to_imgur("path/to/image.png")
    print(f"Image URL: {url}")
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID", "")
IMGUR_UPLOAD_URL = "https://api.imgur.com/3/image"


def upload_to_imgur(image_path, title=None, album=None):
    """
    Upload image to Imgur and return direct URL.
    
    Args:
        image_path: Path to local image file
        title: Optional title for the image
        album: Optional album ID to upload to
        
    Returns:
        dict: Result with success status and URL
    """
    if not IMGUR_CLIENT_ID or IMGUR_CLIENT_ID == "your_imgur_client_id_here":
        return {
            "success": False,
            "error": "IMGUR_CLIENT_ID not set in .env file"
        }
    
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"Image file not found: {image_path}"
        }
    
    headers = {
        "Authorization": f"Client-ID {IMGUR_CLIENT_ID}"
    }
    
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {}
        
        if title:
            data["title"] = title
        if album:
            data["album"] = album
        
        try:
            response = requests.post(IMGUR_UPLOAD_URL, headers=headers, files=files, data=data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                data = result.get("data", {})
                return {
                    "success": True,
                    "url": data.get("link"),  # Direct image URL
                    "id": data.get("id"),
                    "delete_url": data.get("deletehash"),
                    "width": data.get("width"),
                    "height": data.get("height")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("data", {}).get("error", "Upload failed")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }


def upload_from_url(image_url, title=None):
    """
    Upload image from URL to Imgur.
    
    Args:
        image_url: URL of image to upload
        title: Optional title
        
    Returns:
        dict: Result with success status and URL
    """
    if not IMGUR_CLIENT_ID or IMGUR_CLIENT_ID == "your_imgur_client_id_here":
        return {
            "success": False,
            "error": "IMGUR_CLIENT_ID not set in .env file"
        }
    
    headers = {
        "Authorization": f"Client-ID {IMGUR_CLIENT_ID}"
    }
    
    data = {
        "image": image_url
    }
    
    if title:
        data["title"] = title
    
    try:
        response = requests.post(IMGUR_UPLOAD_URL, headers=headers, data=data)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("success"):
            data = result.get("data", {})
            return {
                "success": True,
                "url": data.get("link"),
                "id": data.get("id"),
                "delete_url": data.get("deletehash")
            }
        else:
            return {
                "success": False,
                "error": result.get("data", {}).get("error", "Upload failed")
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


# Test function
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Imgur Uploader - Test")
    print("=" * 60)
    
    if not IMGUR_CLIENT_ID or IMGUR_CLIENT_ID == "your_imgur_client_id_here":
        print("\n[ERROR] IMGUR_CLIENT_ID not configured!")
        print("\nSetup instructions:")
        print("1. Go to: https://api.imgur.com/oauth2/addclient")
        print("2. Register your application")
        print("3. Copy Client ID")
        print("4. Add to .env: IMGUR_CLIENT_ID=your_client_id")
        sys.exit(1)
    
    print(f"\n[OK] Imgur Client ID configured")
    
    # Test with existing image
    test_image = "test_square.png"
    
    if os.path.exists(test_image):
        print(f"\n[TEST] Uploading: {test_image}")
        result = upload_to_imgur(test_image, title="AI Employee Test")
        
        if result.get("success"):
            print(f"\n[OK] Upload successful!")
            print(f"    URL: {result['url']}")
            print(f"    ID: {result['id']}")
            print(f"    Size: {result.get('width', '?')}x{result.get('height', '?')}")
        else:
            print(f"\n[ERROR] Upload failed: {result.get('error')}")
    else:
        print(f"\n[WARN] Test image not found: {test_image}")
        print("Create a test image first or provide image path as argument")
        
        if len(sys.argv) > 1:
            image_path = sys.argv[1]
            print(f"\n[TEST] Uploading: {image_path}")
            result = upload_to_imgur(image_path, title="AI Employee Upload")
            
            if result.get("success"):
                print(f"\n[OK] Upload successful!")
                print(f"    URL: {result['url']}")
            else:
                print(f"\n[ERROR] Upload failed: {result.get('error')}")
