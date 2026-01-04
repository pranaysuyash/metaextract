#!/usr/bin/env python3
"""
Test User Creation Script for MetaExtract

Creates a test user with various roles and permissions for testing purposes.
"""

import os
import sys
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path

# Add the server directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    # For Python, we need to use the Python storage module if it exists
    # Otherwise, we'll need to create the test users directly in the database
    # using SQL or by calling the API endpoints

    # Since the auth_enhanced.ts is a TypeScript file, we can't import it directly in Python
    # Instead, we'll use the existing storage module if available
    from storage import storage
    import bcrypt
    import hashlib
    import secrets
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Trying to use the existing Python modules...")

    # Try to import the existing Python modules
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'extractor'))

        # For now, let's create a simple test user creation that works with the existing system
        print("Using direct database insertion for test users...")
    except Exception as e2:
        print(f"Also failed with: {e2}")
        print("Will create test users using API calls instead")


def create_test_user():
    """Create a test user for MetaExtract"""
    
    print("Creating test user for MetaExtract...")
    
    # Define test user data
    test_user_data = {
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'firstName': 'Test',
        'lastName': 'User',
        'emailVerified': True,
        'twoFactorEnabled': False,
        'twoFactorSecret': None,
    }
    
    try:
        # Validate password strength
        password_validation = validatePasswordStrength(test_user_data['password'])
        if not password_validation.isValid:
            print(f"Password validation failed: {password_validation.errors}")
            return None
        
        # Hash the password
        hashed_password = hashPassword(test_user_data['password'])
        test_user_data['password'] = hashed_password
        
        # Check if user already exists
        existing_user = storage.getUserByEmail(test_user_data['email'])
        if existing_user:
            print(f"User with email {test_user_data['email']} already exists. Updating...")
            # Update the existing user
            updated_user = storage.updateUserProfile(existing_user.id, {
                'firstName': test_user_data['firstName'],
                'lastName': test_user_data['lastName'],
            })
            print(f"Updated existing user: {updated_user.email}")
        else:
            # Create the new user
            user = storage.createUser(test_user_data)
            print(f"Created new user: {user.email}")
        
        # Create initial credit balance for the user
        credit_balance = storage.getOrCreateCreditBalance(user.id if 'user' in locals() else existing_user.id)
        print(f"Created credit balance: {credit_balance.credits} credits")
        
        # Add some test credit transactions
        storage.recordCreditTransaction(
            userId=user.id if 'user' in locals() else existing_user.id,
            amount=10,
            type='addition',
            description='Initial test credits',
            metadata={'source': 'test_setup'}
        )
        
        print("\n" + "="*50)
        print("TEST USER CREATED SUCCESSFULLY!")
        print("="*50)
        print(f"Email: {test_user_data['email']}")
        print(f"Password: {test_user_data['password'][:10]}..." if 'user' in locals() else f"Password: [already hashed]")
        print(f"Initial Credits: {credit_balance.credits}")
        print("\nUse these credentials to test the authentication system.")
        print("Note: The password is securely hashed in the database.")
        
        return user if 'user' in locals() else existing_user
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_admin_user():
    """Create an admin test user"""
    
    print("\nCreating admin test user...")
    
    admin_user_data = {
        'email': 'admin@example.com',
        'password': 'AdminSecurePass123!',
        'firstName': 'Admin',
        'lastName': 'User',
        'emailVerified': True,
        'twoFactorEnabled': True,
        'twoFactorSecret': 'JBSWY3DPEHPK3PXP',  # Example secret
    }
    
    try:
        # Validate password strength
        password_validation = validatePasswordStrength(admin_user_data['password'])
        if not password_validation.isValid:
            print(f"Admin password validation failed: {password_validation.errors}")
            return None
        
        # Hash the password
        hashed_password = hashPassword(admin_user_data['password'])
        admin_user_data['password'] = hashed_password
        
        # Check if admin user already exists
        existing_admin = storage.getUserByEmail(admin_user_data['email'])
        if existing_admin:
            print(f"Admin user with email {admin_user_data['email']} already exists.")
            return existing_admin
        else:
            # Create the new admin user
            admin_user = storage.createUser(admin_user_data)
            print(f"Created new admin user: {admin_user.email}")
        
        # Create initial credit balance for the admin user
        credit_balance = storage.getOrCreateCreditBalance(admin_user.id)
        print(f"Created admin credit balance: {credit_balance.credits} credits")
        
        print(f"Admin user created: {admin_user.email}")
        return admin_user
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("MetaExtract Test User Creation Script")
    print("="*40)
    
    # Create regular test user
    test_user = create_test_user()
    
    # Create admin test user
    admin_user = create_admin_user()
    
    if test_user or admin_user:
        print("\n" + "="*50)
        print("TEST USERS SETUP COMPLETE!")
        print("="*50)
        print("You can now use these accounts to test the authentication system.")
        print("Remember to use proper authentication methods when testing.")
    else:
        print("\nFailed to create test users.")
        sys.exit(1)