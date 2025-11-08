#!/usr/bin/env python
"""
Publish test events to RabbitMQ for testing consumers.

Usage:
    python scripts/publish_test_events.py --event auth
    python scripts/publish_test_events.py --event document
"""

import sys
import os
import django
import argparse
import uuid
from datetime import datetime

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from infrastructure.rabbitmq.producer import get_rabbitmq_producer


def publish_auth_registration_event():
    """Publish a test auth.user.registered event."""
    
    event_data = {
        'messageId': str(uuid.uuid4()),
        'idCitizen': 12345678,
        'name': 'Juan Pérez',
        'email': 'juan.perez@example.com',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    print("=" * 70)
    print("PUBLISHING AUTH.USER.REGISTERED EVENT")
    print("=" * 70)
    print()
    print("Event Data:")
    print("-" * 70)
    for key, value in event_data.items():
        print(f"  {key}: {value}")
    print()
    
    producer = get_rabbitmq_producer()
    producer.publish_event('auth.user.registered', event_data)
    
    print("✅ Event published successfully!")
    print("=" * 70)


def publish_document_auth_event():
    """Publish a test document.authentication.requested event."""
    
    event_data = {
        'messageId': str(uuid.uuid4()),
        'documentId': f'doc-{uuid.uuid4().hex[:8]}',
        'idCitizen': 12345678,
        'urlDocument': 'https://example.com/documents/test-document.pdf',
        'documentTitle': 'test-document.pdf'
    }
    
    print("=" * 70)
    print("PUBLISHING DOCUMENT.AUTHENTICATION.REQUESTED EVENT")
    print("=" * 70)
    print()
    print("Event Data:")
    print("-" * 70)
    for key, value in event_data.items():
        print(f"  {key}: {value}")
    print()
    
    producer = get_rabbitmq_producer()
    producer.publish_event('document.authentication.requested', event_data)
    
    print("✅ Event published successfully!")
    print("=" * 70)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Publish test events to RabbitMQ')
    parser.add_argument(
        '--event',
        type=str,
        choices=['auth', 'document'],
        required=True,
        help='Type of event to publish (auth or document)'
    )
    
    args = parser.parse_args()
    
    if args.event == 'auth':
        publish_auth_registration_event()
    elif args.event == 'document':
        publish_document_auth_event()
