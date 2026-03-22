#!/usr/bin/env python3
"""
Create Test Image using Playwright
"""

from playwright.sync_api import sync_playwright

print("Creating test image using Playwright...")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Create a simple canvas and save as image
    page.goto("data:text/html,<canvas id='c' width='1080' height='1080'></canvas><script>var c=document.getElementById('c'),x=c.getContext('2d');x.fillStyle='#496D89';x.fillRect(0,0,1080,1080);x.fillStyle='white';x.font='48px Arial';x.fillText('AI Employee Test',100,540);x.fillText('Gold Tier',100,600);</script>")
    page.screenshot(path='post_image.png', clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1080})
    browser.close()

print("Test image created: post_image.png")
