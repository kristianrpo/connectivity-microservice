"""
Consumer for auth.user.registered events.

CORE FUNCTIONALITY #2: Listen to auth events and register citizens.
"""

import logging
from django.core.management.base import BaseCommand
from django.conf import settings

from infrastructure.rabbitmq.consumer import RabbitMQConsumer
from apps.citizen_registration.services import CitizenRegistrationService

logger = logging.getLogger(__name__)


class AuthUserRegisteredConsumer(RabbitMQConsumer):
    """Consumer for auth.user.registered events."""
    
    def __init__(self):
        super().__init__(
            queue_name='auth.user.registered',
            routing_key='auth.user.registered'
        )
        self.registration_service = CitizenRegistrationService()
    
    def process_message(self, body: dict):
        """Process auth.user.registered event and register citizen."""
        try:
            message_id = body.get('messageId')
            id_citizen = body.get('idCitizen')
            name = body.get('name')
            email = body.get('email')
            timestamp = body.get('timestamp')
            
            if not all([message_id, id_citizen, name, email, timestamp]):
                logger.error(f"Missing fields in event: {body}")
                return
            
            logger.info(f"📝 Processing registration for citizen {id_citizen}: {name}")
            
            self.registration_service.process_auth_registration_event(
                message_id=message_id,
                id_citizen=id_citizen,
                name=name,
                email=email,
                timestamp=timestamp
            )
            
            logger.info(f"✅ Citizen {id_citizen} processed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error processing event: {str(e)}", exc_info=True)
            raise


class Command(BaseCommand):
    """Start auth events consumer."""
    
    help = 'Consume auth.user.registered events'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--routing-key',
            type=str,
            default='auth.user.registered',
            help='Routing key (default: auth.user.registered)'
        )
    
    def handle(self, *args, **options):
        routing_key = options['routing_key']
        
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("AUTH REGISTRATION CONSUMER"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"Routing key: {routing_key}")
        self.stdout.write(f"Exchange: {settings.RABBITMQ_EXCHANGE}")
        self.stdout.write("=" * 70)
        
        try:
            consumer = AuthUserRegisteredConsumer()
            if routing_key != 'auth.user.registered':
                consumer.routing_key = routing_key
                consumer.queue_name = routing_key
            
            consumer.start_consuming()
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nShutting down..."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nError: {str(e)}"))
            raise
