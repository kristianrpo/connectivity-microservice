"""
Consumer for document.authentication.requested events.

CORE FUNCTIONALITY #3: Listen to document events and authenticate them.
"""

import logging
from django.core.management.base import BaseCommand
from django.conf import settings

from infrastructure.rabbitmq.consumer import RabbitMQConsumer
from apps.document_authentication.services import DocumentAuthenticationService

logger = logging.getLogger(__name__)


class DocumentAuthenticationConsumer(RabbitMQConsumer):
    """Consumer for document.authentication.requested events."""
    
    def __init__(self):
        super().__init__(
            queue_name='document.authentication.requested',
            routing_key='document.authentication.requested'
        )
        self.auth_service = DocumentAuthenticationService()
    
    def process_message(self, body: dict):
        """Process document.authentication.requested event."""
        try:
            message_id = body.get('messageId')
            document_id = body.get('documentId')
            id_citizen = body.get('idCitizen')
            url_document = body.get('urlDocument')
            document_title = body.get('documentTitle')
            
            if not all([message_id, document_id, id_citizen, url_document, document_title]):
                logger.error(f"Missing fields in event: {body}")
                return
            
            logger.info(f"📄 Processing document {document_id} for citizen {id_citizen}: {document_title}")
            
            result = self.auth_service.process_authentication_request(
                message_id=message_id,
                document_id=document_id,
                id_citizen=id_citizen,
                url_document=url_document,
                document_title=document_title
            )
            
            if result.authenticated:
                logger.info(f"✅ Document {document_id} authenticated successfully")
            else:
                logger.warning(f"❌ Document {document_id} authentication failed: {result.message}")
            
        except Exception as e:
            logger.error(f"❌ Error processing event: {str(e)}", exc_info=True)
            raise


class Command(BaseCommand):
    """Start document authentication consumer."""
    
    help = 'Consume document.authentication.requested events'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--routing-key',
            type=str,
            default='document.authentication.requested',
            help='Routing key (default: document.authentication.requested)'
        )
    
    def handle(self, *args, **options):
        routing_key = options['routing_key']
        
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("DOCUMENT AUTHENTICATION CONSUMER"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"Routing key: {routing_key}")
        self.stdout.write(f"Exchange: {settings.RABBITMQ_EXCHANGE}")
        self.stdout.write("=" * 70)
        
        try:
            consumer = DocumentAuthenticationConsumer()
            if routing_key != 'document.authentication.requested':
                consumer.routing_key = routing_key
                consumer.queue_name = routing_key
            
            consumer.start_consuming()
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nShutting down..."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nError: {str(e)}"))
            raise
