#!/usr/bin/env python3
"""
Gmail OAuth2 Pre-Validation Script

This script validates Gmail OAuth2 setup before agent implementation begins.
It provides step-by-step guidance for credential setup and tests API access.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# File paths
CREDENTIALS_DIR = Path("credentials")
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"


def print_step(step: int, title: str, success: bool = True):
    """Print a formatted step with status."""
    status = "✅" if success else "❌"
    print(f"\n{status} Step {step}: {title}")


def print_error(message: str):
    """Print an error message."""
    print(f"❌ ERROR: {message}")


def print_success(message: str):
    """Print a success message."""
    print(f"✅ SUCCESS: {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ️  {message}")


def check_credentials_directory() -> bool:
    """Check if credentials directory exists."""
    print_step(1, "Checking credentials directory")
    
    if not CREDENTIALS_DIR.exists():
        print_error(f"Credentials directory '{CREDENTIALS_DIR}' does not exist")
        print("Creating credentials directory...")
        CREDENTIALS_DIR.mkdir(exist_ok=True)
        print_success(f"Created credentials directory: {CREDENTIALS_DIR}")
    else:
        print_success(f"Credentials directory exists: {CREDENTIALS_DIR}")
    
    return True


def check_credentials_file() -> bool:
    """Check if credentials.json exists and is valid."""
    print_step(2, "Checking credentials.json file")
    
    if not CREDENTIALS_FILE.exists():
        print_error(f"Credentials file '{CREDENTIALS_FILE}' not found")
        print("\n📋 SETUP INSTRUCTIONS:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Create a new project or select an existing one")
        print("3. Enable the Gmail API:")
        print("   - Go to 'APIs & Services' > 'Library'")
        print("   - Search for 'Gmail API' and enable it")
        print("4. Create OAuth2 credentials:")
        print("   - Go to 'APIs & Services' > 'Credentials'")
        print("   - Click 'Create Credentials' > 'OAuth client ID'")
        print("   - Choose 'Desktop application'")
        print("   - Download the JSON file")
        print(f"5. Save the downloaded file as: {CREDENTIALS_FILE}")
        print("\nRun this script again after completing the setup.")
        return False
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds_data = json.load(f)
        
        # Validate structure
        if 'installed' not in creds_data:
            print_error("Invalid credentials.json format - missing 'installed' section")
            return False
        
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
        for field in required_fields:
            if field not in creds_data['installed']:
                print_error(f"Invalid credentials.json - missing '{field}' in 'installed' section")
                return False
        
        print_success("credentials.json file is valid")
        return True
        
    except json.JSONDecodeError:
        print_error("credentials.json is not valid JSON")
        return False
    except Exception as e:
        print_error(f"Error reading credentials.json: {e}")
        return False


def authenticate_gmail() -> Optional[Credentials]:
    """Authenticate with Gmail API and return credentials."""
    print_step(3, "Authenticating with Gmail API")
    
    creds = None
    
    # Check if token.json exists
    if TOKEN_FILE.exists():
        print_info("Found existing token.json, attempting to use...")
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            print_error(f"Error loading existing token: {e}")
            print_info("Will create new token...")
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print_info("Refreshing expired token...")
            try:
                creds.refresh(Request())
                print_success("Token refreshed successfully")
            except Exception as e:
                print_error(f"Error refreshing token: {e}")
                creds = None
        
        if not creds:
            print_info("Starting OAuth2 flow...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES
                )
                creds = flow.run_local_server(port=0)
                print_success("OAuth2 authentication completed")
            except Exception as e:
                print_error(f"OAuth2 authentication failed: {e}")
                return None
        
        # Save the credentials for the next run
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            print_success(f"Saved token to: {TOKEN_FILE}")
        except Exception as e:
            print_error(f"Error saving token: {e}")
    
    return creds


def test_gmail_api(creds: Credentials) -> bool:
    """Test Gmail API access."""
    print_step(4, "Testing Gmail API access")
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Test 1: Get user profile
        print_info("Testing: Get user profile...")
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')
        print_success(f"Connected to Gmail account: {email}")
        
        # Test 2: List labels (basic read access)
        print_info("Testing: List labels...")
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        print_success(f"Found {len(labels)} labels in mailbox")
        
        # Test 3: Create a draft (write access)
        print_info("Testing: Create test draft...")
        draft_body = {
            'message': {
                'raw': 'VGVzdCBkcmFmdCBmcm9tIFB5ZGFudGljQUkgdmFsaWRhdGlvbg=='  # Base64: "Test draft from PydanticAI validation"
            }
        }
        
        draft = service.users().drafts().create(userId='me', body=draft_body).execute()
        draft_id = draft.get('id')
        print_success(f"Created test draft with ID: {draft_id}")
        
        # Clean up: Delete the test draft
        print_info("Cleaning up: Deleting test draft...")
        service.users().drafts().delete(userId='me', id=draft_id).execute()
        print_success("Test draft deleted successfully")
        
        return True
        
    except HttpError as e:
        print_error(f"Gmail API error: {e}")
        if e.resp.status == 403:
            print_info("Possible causes:")
            print("- Gmail API not enabled in Google Cloud Console")
            print("- Insufficient OAuth2 scopes")
            print("- Account access restrictions")
        return False
    except Exception as e:
        print_error(f"Unexpected error testing Gmail API: {e}")
        return False


def validate_environment_variables() -> bool:
    """Validate required environment variables."""
    print_step(5, "Checking environment variables")
    
    required_vars = ['LLM_API_KEY', 'BRAVE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print_error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("\n📋 ENVIRONMENT SETUP:")
        print("1. Copy .env.example to .env")
        print("2. Fill in the required API keys:")
        for var in missing_vars:
            print(f"   - {var}=your_key_here")
        print("3. Source the environment or restart your terminal")
        return False
    
    print_success("All required environment variables are set")
    return True


def main():
    """Main validation function."""
    print("🔐 Gmail OAuth2 Pre-Validation Script")
    print("=" * 50)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Check credentials directory
    if check_credentials_directory():
        success_count += 1
    
    # Step 2: Check credentials.json
    if not check_credentials_file():
        print("\n❌ VALIDATION FAILED: Missing or invalid credentials.json")
        print("Complete the setup instructions above and run this script again.")
        sys.exit(1)
    success_count += 1
    
    # Step 3: Authenticate with Gmail
    creds = authenticate_gmail()
    if not creds:
        print("\n❌ VALIDATION FAILED: Gmail authentication failed")
        sys.exit(1)
    success_count += 1
    
    # Step 4: Test Gmail API
    if not test_gmail_api(creds):
        print("\n❌ VALIDATION FAILED: Gmail API test failed")
        sys.exit(1)
    success_count += 1
    
    # Step 5: Check environment variables
    if not validate_environment_variables():
        print("\n❌ VALIDATION FAILED: Environment variables not set")
        sys.exit(1)
    success_count += 1
    
    # Success summary
    print("\n" + "=" * 50)
    print(f"🎉 VALIDATION SUCCESSFUL! ({success_count}/{total_steps} steps completed)")
    print("\n✅ Gmail OAuth2 setup is ready for agent implementation")
    print("✅ All required permissions verified")
    print("✅ Environment configuration validated")
    print("\nYou can now proceed with implementing the PydanticAI agents!")


if __name__ == "__main__":
    main()