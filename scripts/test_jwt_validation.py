#!/usr/bin/env python
"""
Test script for JWT token validation.

Usage:
    python scripts/test_jwt_validation.py <token>
    
Example:
    python scripts/test_jwt_validation.py eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
"""

import sys
import os
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

import jwt
from django.conf import settings
from infrastructure.auth import get_oauth2_validator


def test_token_validation(token: str):
    """Test JWT token validation."""
    print("=" * 70)
    print("JWT TOKEN VALIDATION TEST")
    print("=" * 70)
    print()
    
    # Get validator
    validator = get_oauth2_validator()
    
    print(f"JWT Secret: {validator.jwt_secret[:10]}... (truncated)")
    print(f"JWT Algorithm: {validator.jwt_algorithm}")
    print()
    
    # Validate token
    print("Validating token...")
    result = validator.validate_token(token)
    
    print()
    print("Validation Result:")
    print("-" * 70)
    
    if result['valid']:
        print("✅ Token is VALID")
        print()
        print(f"Client ID: {result.get('client_id')}")
        print(f"Scope: {result.get('scope')}")
        print(f"Expires at: {result.get('exp')}")
    else:
        print("❌ Token is INVALID")
        print()
        print(f"Error: {result.get('error')}")
    
    print()
    print("=" * 70)
    
    # Try to decode manually for debugging
    print()
    print("Manual JWT Decode (for debugging):")
    print("-" * 70)
    
    try:
        # Decode without verification to see payload
        payload = jwt.decode(token, options={"verify_signature": False})
        print("Token Payload:")
        for key, value in payload.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error decoding token: {e}")
    
    print()
    print("=" * 70)


def generate_test_token():
    """Generate a test token for development."""
    print("=" * 70)
    print("GENERATE TEST TOKEN")
    print("=" * 70)
    print()
    
    import time
    from datetime import datetime, timedelta
    
    secret = settings.AUTH_SERVICE_JWT_SECRET
    
    payload = {
        'client_id': 'test-client',
        'grant_type': 'client_credentials',
        'scope': 'read:citizens',
        'exp': int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        'iat': int(datetime.utcnow().timestamp())
    }
    
    token = jwt.encode(payload, secret, algorithm='HS256')
    
    print("Generated Test Token:")
    print("-" * 70)
    print(token)
    print()
    print("Payload:")
    for key, value in payload.items():
        if key == 'exp' or key == 'iat':
            dt = datetime.fromtimestamp(value)
            print(f"  {key}: {value} ({dt})")
        else:
            print(f"  {key}: {value}")
    
    print()
    print("=" * 70)
    print()
    print("Test this token with:")
    print(f"  python scripts/test_jwt_validation.py {token}")
    print()
    
    return token


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_jwt_validation.py <token>")
        print("   or: python scripts/test_jwt_validation.py --generate")
        print()
        sys.exit(1)
    
    if sys.argv[1] == '--generate':
        token = generate_test_token()
        print()
        print("Now testing the generated token...")
        print()
        test_token_validation(token)
    else:
        token = sys.argv[1]
        test_token_validation(token)
