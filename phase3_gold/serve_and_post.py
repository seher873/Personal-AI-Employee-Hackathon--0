#!/usr/bin/env python3
"""
Serve local image temporarily and post using Instagram API
"""
import sys
import os
import threading
import time
import requests
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Skills'))

from skill_instagram_api import InstagramAPISkill

def find_free_port():
    """Find a free port to serve the image"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_server(image_path, host='localhost'):
    """Start a temporary HTTP server to serve the image"""
    port = find_free_port()
    server_url = f"http://{host}:{port}/{os.path.basename(image_path)}"

    # Change to the directory containing the image
    os.chdir(os.path.dirname(os.path.abspath(image_path)) or '.')

    # Create the server
    server = HTTPServer((host, port), SimpleHTTPRequestHandler)

    print(f"Started temporary server: {server_url}")
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # Wait a moment for server to start
    time.sleep(1)

    return server, server_url

def test_post_with_temp_server():
    print("Setting up temporary image server to make image accessible...")

    image_path = "post_image.png"
    if not os.path.exists(image_path):
        print(f"ERROR: {image_path} not found!")
        return

    server, server_url = start_server(image_path)

    try:
        print(f"Image should be accessible at: {server_url}")

        # Test if the image is accessible
        try:
            response = requests.get(server_url, timeout=5)
            if response.status_code == 200:
                print("OK Image is accessible via temporary server")
            else:
                print(f"FAIL Image not accessible: HTTP {response.status_code}")
                return
        except requests.RequestException as e:
            print(f"FAIL Error accessing image: {e}")
            return

        # Now try to post using the temporary server URL
        print("\nAttempting Instagram post with temporary image URL...")
        ig = InstagramAPISkill()

        caption = "Test post from AI Employee Vault! Served from temporary server. #AI #Automation #Testing #Success"

        result = ig.post(caption, server_url)
        print(f"Post Result: {result}")

        if result.get('success'):
            print(f"🎉 SUCCESS! Your post was published to Instagram!")
            print(f"Post ID: {result.get('post_id')}")
        else:
            print(f"❌ Post failed: {result.get('error')}")

    finally:
        print("Stopping temporary server...")
        server.shutdown()

if __name__ == "__main__":
    print("Instagram API Post with Temporary Image Server")
    print("="*60)
    test_post_with_temp_server()