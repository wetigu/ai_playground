#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for the Tigu B2B application
"""

import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(length)

def generate_hex_key(length=32):
    """Generate a secure random hex key"""
    return secrets.token_hex(length)

def generate_alphanumeric_key(length=50):
    """Generate a secure alphanumeric key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    print("=" * 60)
    print("SECRET_KEY Generator for Tigu B2B Application")
    print("=" * 60)
    print()
    
    print("Option 1 - URL-safe base64 encoded (Recommended):")
    key1 = generate_secret_key(32)
    print(f"SECRET_KEY={key1}")
    print()
    
    print("Option 2 - Hexadecimal:")
    key2 = generate_hex_key(32)
    print(f"SECRET_KEY={key2}")
    print()
    
    print("Option 3 - Alphanumeric:")
    key3 = generate_alphanumeric_key(50)
    print(f"SECRET_KEY={key3}")
    print()
    
    print("=" * 60)
    print("Copy one of the SECRET_KEY values above to your .env file")
    print("Recommendation: Use Option 1 (URL-safe base64)")
    print("=" * 60) 