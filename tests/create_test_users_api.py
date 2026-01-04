#!/usr/bin/env python3
"""
Test Script to Create Test Users via API for MetaExtract

This script creates test users by calling the actual API endpoints
instead of trying to directly access the database.
"""

import os
import sys
import requests
import json
from pathlib import Path

def create_test_users_via_api():
    """Create test users by calling the API endpoints"""
    
    print("Creating test users via API...")
    
    # Get the base URL from environment or use default
    base_url = os.getenv('METAEXTRACT_API_URL', 'http://localhost:3000')
    
    print(f"Using API URL: {base_url}")
    
    # Test user credentials
    test_users = [
        {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'SecurePass123!'
        },
        {
            'email': 'admin@example.com',
            'username': 'adminuser',
            'password': 'AdminSecurePass123!'
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        print(f"\nCreating user: {user_data['email']}")
        
        # Try to register the user
        try:
            response = requests.post(
                f"{base_url}/api/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                print(f"✅ User {user_data['email']} created successfully")
                created_users.append(user_data)
            elif response.status_code == 409:
                # User already exists, which is fine
                print(f"⚠️  User {user_data['email']} already exists")
                created_users.append(user_data)
            else:
                print(f"❌ Failed to create user {user_data['email']}: {response.status_code} - {response.text}")
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API at {base_url}")
            print("Make sure the MetaExtract server is running")
            return False
        except Exception as e:
            print(f"❌ Error creating user {user_data['email']}: {e}")
            return False
    
    if created_users:
        print(f"\n✅ Successfully prepared {len(created_users)} test users")
        print("\nTest user credentials:")
        for user in created_users:
            print(f"- Email: {user['email']}, Password: {user['password']}")
        print("\nYou can now use these credentials to test the authentication system.")
        return True
    else:
        print("\n❌ No test users were created")
        return False

def test_login():
    """Test login with the created users"""
    
    base_url = os.getenv('METAEXTRACT_API_URL', 'http://localhost:3000')
    
    test_credentials = [
        ('test@example.com', 'SecurePass123!'),
        ('admin@example.com', 'AdminSecurePass123!')
    ]
    
    print("\nTesting login with test users...")
    
    for email, password in test_credentials:
        print(f"\nTesting login for {email}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/auth/login",
                json={'email': email, 'password': password, 'tier': 'enterprise'},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"✅ Login successful for {email}")
                # Optionally store the token for further testing
                data = response.json()
                if 'token' in data:
                    print(f"   Token received (length: {len(data['token'])})")
            elif response.status_code == 401:
                print(f"❌ Login failed for {email}: Invalid credentials")
            else:
                print(f"? Login response for {email}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing login for {email}: {e}")

if __name__ == "__main__":
    print("MetaExtract Test User Creation via API")
    print("="*50)
    
    success = create_test_users_via_api()
    
    if success:
        print("\n" + "="*50)
        print("TESTING LOGIN WITH CREATED USERS")
        print("="*50)
        test_login()
        
        print("\n" + "="*50)
        print("TEST USER CREATION AND VERIFICATION COMPLETE")
        print("="*50)
        print("You can now use these credentials to test the authentication system:")
        print("- Email: test@example.com, Password: SecurePass123!")
        print("- Email: admin@example.com, Password: AdminSecurePass123!")
    else:
        print("\n❌ Test user creation failed")
        sys.exit(1)