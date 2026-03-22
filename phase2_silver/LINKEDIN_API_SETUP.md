# LinkedIn API Setup Guide

## Problem
Your current access token doesn't have the required permissions to post to LinkedIn.

## Solution: Get Proper Token with Scopes

### Step 1: Create LinkedIn App
1. Go to: https://www.linkedin.com/developers/apps
2. Click "Create app"
3. Select your company page
4. Fill in app details

### Step 2: Request Required Permissions
For **Personal Profile Posts**:
- `w_member_social` - Write posts to your profile

For **Company Page Posts**:
- `w_organization_social` - Write posts to company pages
- `r_organization_social` - Read organization data
- You must be an **admin** of the company page

### Step 3: Get Access Token

#### Option A: Using OAuth Flow (Recommended)
```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=w_member_social%20w_organization_social
```

#### Option B: Using Existing Credentials
Your `.env` already has:
```
Linkedin_Client_ID =YOUR_CLIENT_ID
Linkedin_Client_Secret =YOUR_CLIENT_SECRET
```

Use these to generate a new token with proper scopes.

### Step 4: Test Token
```bash
# Test personal post
py -3 linkedin_api_poster.py --text "Hello from API!"

# Test company post
py -3 linkedin_api_poster.py --company --text "Hello from Company!"
```

## Current Token Issues
Your token `AQX7UtR8FpLArPgs7o8h_c2Rg4fWKvFqUQ1alnG1X2rh2dLqxwA4PmHViRyEkq3lO782hQVrAPUY9KSf7shSKx1hMHC2NBblW1Q820HA2ZGl0TRPMi5PeAjYwpSRaJ_bOz_zFAB3LY3acfSh-ecl9DIrmXJU6csfpKhmnaanVKKmk9DcPRXEAoHx-e5N2OWYpfZhce515DvRCs_An0c-7WhVHYbRdBwYWi2kicPAyGDEFuzaJI68thjfoMxyvQOGSkigqunSew3K7plGBIJUxu6r9-GFL5pdYFO1H2uuv_cJre1w2r73XvemARCCnEdF3lROJqjLW_UQMWCyShqMm0zZVuUunA`

Error received:
```
ACCESS_DENIED - Not enough permissions to access
```

This means the token was created without `w_member_social` or `w_organization_social` scopes.

## Alternative: Use Browser Poster
If API access is not available, use the browser-based poster:
```bash
py -3 linkedin_browser_poster.py --text "Your post text"
```

## Files Created
- `linkedin_api_poster.py` - New API-based poster
- `linkedin_browser_poster.py` - Existing browser automation poster

## Usage Examples

### Text Post (Personal)
```bash
py -3 linkedin_api_poster.py --text "Your post content here"
```

### Text Post (Company)
```bash
py -3 linkedin_api_poster.py --company --text "Company announcement"
```

### Post with Image
```bash
py -3 linkedin_api_poster.py --image path/to/image.jpg --text "Check this out!"
```

### Post from File
```bash
py -3 linkedin_api_poster.py --file Post_Ideas.md --company
```
