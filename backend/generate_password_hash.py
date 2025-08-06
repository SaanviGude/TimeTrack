#!/usr/bin/env python3
"""
Password hash generator
Creates a new bcrypt hash for a password
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils import get_password_hash

def generate_hash():
    """Generate a new password hash"""
    print("Password Hash Generator")
    print("=" * 30)
    
    # Get password from user
    password = input("Enter new password: ").strip()
    
    if not password:
        print("❌ Password cannot be empty")
        return
    
    if len(password) < 6:
        print("❌ Password should be at least 6 characters")
        return
    
    # Generate hash
    try:
        hashed_password = get_password_hash(password)
        print(f"\n✅ Password hash generated:")
        print(f"Hash: {hashed_password}")
        print(f"\n📝 To update in database, run:")
        print(f"UPDATE users SET hashed_password = '{hashed_password}' WHERE email = 'your_email@example.com';")
        
    except Exception as e:
        print(f"❌ Error generating hash: {e}")

if __name__ == "__main__":
    generate_hash()
