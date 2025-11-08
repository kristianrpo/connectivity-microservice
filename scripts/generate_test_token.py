#!/usr/bin/env python
"""
Generate a test JWT token for OAuth2 Client Credentials.

Usage:
    python scripts/generate_test_token.py
"""

import sys
import os
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

import jwt
from datetime import datetime, timedelta
from django.conf import settings


def generate_token(client_id='auth-microservice', hours=24):
    """Generate a test OAuth2 Client Credentials token."""
    
    secret = settings.AUTH_SERVICE_JWT_SECRET
    algorithm = settings.AUTH_SERVICE_JWT_ALGORITHM
    
    payload = {
        'client_id': client_id,
        'grant_type': 'client_credentials',
        'scope': 'read:citizens write:citizens',
        'exp': int((datetime.utcnow() + timedelta(hours=hours)).timestamp()),
        'iat': int(datetime.utcnow().timestamp())
    }
    
    token = jwt.encode(payload, secret, algorithm=algorithm)
    
    print("=" * 70)
    print("OAUTH2 CLIENT CREDENTIALS TOKEN GENERATED")
    print("=" * 70)
    print()
    print("Token:")
    print("-" * 70)
    print(token)
    print()
    print("Payload:")
    print("-" * 70)
    for key, value in payload.items():
        if key in ['exp', 'iat']:
            dt = datetime.fromtimestamp(value)
            print(f"  {key}: {value} ({dt})")
        else:
            print(f"  {key}: {value}")
    print()
    print("=" * 70)
    print()
    print("Test with curl:")
    print("-" * 70)
    print(f'curl -H "Authorization: Bearer {token}" \\')
    print('     http://localhost:8000/api/external-connectivity/external/citizens/12345678/exists/')
    print()
    print("=" * 70)
    
    return token


if __name__ == '__main__':
    generate_token()
