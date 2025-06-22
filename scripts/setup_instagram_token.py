#!/usr/bin/env python3
"""
Instagram Access Token Setup Script
This script helps you generate a Facebook app access token for Instagram oEmbed API
"""

import asyncio
import httpx
import os
from urllib.parse import urlencode

def get_app_credentials():
    """Get Facebook app credentials from user input"""
    print("=== Instagram Access Token Setup ===")
    print("You need a Facebook App to access Instagram oEmbed API")
    print("Create one at: https://developers.facebook.com/\n")
    
    app_id = input("Enter your Facebook App ID: ").strip()
    if not app_id:
        print("❌ App ID is required")
        return None, None
    
    app_secret = input("Enter your Facebook App Secret: ").strip()
    if not app_secret:
        print("❌ App Secret is required")
        return None, None
    
    return app_id, app_secret

async def generate_app_access_token(app_id: str, app_secret: str) -> str:
    """Generate app access token using Facebook Graph API"""
    try:
        async with httpx.AsyncClient() as client:
            url = "https://graph.facebook.com/oauth/access_token"
            params = {
                "client_id": app_id,
                "client_secret": app_secret,
                "grant_type": "client_credentials"
            }
            
            print(f"🔄 Generating access token...")
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                if access_token:
                    print("✅ Access token generated successfully!")
                    return access_token
                else:
                    print("❌ No access token in response")
                    return None
            else:
                print(f"❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Network error: {e}")
        return None

async def test_access_token(access_token: str) -> bool:
    """Test the access token with a sample Instagram URL"""
    try:
        async with httpx.AsyncClient() as client:
            # Use a well-known public Instagram post for testing
            test_url = "https://www.instagram.com/p/CK4tYUjF8VZ/"  # Sample public post
            
            url = "https://graph.facebook.com/v18.0/instagram_oembed"
            params = {
                "url": test_url,
                "access_token": access_token,
                "omitscript": False
            }
            
            print(f"🔄 Testing access token...")
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                print("✅ Access token works correctly!")
                return True
            else:
                print(f"⚠️ Test failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def update_env_file(app_id: str, app_secret: str, access_token: str):
    """Update the .env file with the credentials"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env")
    
    # Read existing .env file
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_lines = f.readlines()
    
    # Remove existing Instagram/Facebook entries
    env_lines = [line for line in env_lines if not any(
        key in line for key in [
            'FACEBOOK_APP_ID=',
            'FACEBOOK_APP_SECRET=',
            'FACEBOOK_APP_ACCESS_TOKEN=',
            'INSTAGRAM_ACCESS_TOKEN='
        ]
    )]
    
    # Add new entries
    env_lines.append(f"\n# Instagram/Facebook Configuration\n")
    env_lines.append(f"FACEBOOK_APP_ID={app_id}\n")
    env_lines.append(f"FACEBOOK_APP_SECRET={app_secret}\n")
    env_lines.append(f"FACEBOOK_APP_ACCESS_TOKEN={access_token}\n")
    
    # Write back to .env file
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    with open(env_path, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Updated {env_path}")

async def main():
    """Main setup flow"""
    print("This script will help you set up Instagram API access for Recipe Reel Manager\n")
    
    # Get app credentials
    app_id, app_secret = get_app_credentials()
    if not app_id or not app_secret:
        return
    
    # Generate access token
    access_token = await generate_app_access_token(app_id, app_secret)
    if not access_token:
        print("\n❌ Failed to generate access token")
        print("Please check your App ID and Secret are correct")
        return
    
    # Test the token
    if await test_access_token(access_token):
        print(f"\n📋 Your access token: {access_token}")
        
        # Ask if user wants to update .env file
        update_env = input("\nUpdate backend/.env file automatically? (y/n): ").lower().strip()
        if update_env in ['y', 'yes']:
            update_env_file(app_id, app_secret, access_token)
        else:
            print("\n📝 Add these to your backend/.env file:")
            print(f"FACEBOOK_APP_ID={app_id}")
            print(f"FACEBOOK_APP_SECRET={app_secret}")
            print(f"FACEBOOK_APP_ACCESS_TOKEN={access_token}")
    
    print("\n🎉 Setup complete!")
    print("Your Instagram oEmbed API should now work correctly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")