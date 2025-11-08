"""
RabbitMQ producer for publishing events.
"""

import json
import logging
import pika
from django.conf import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RabbitMQProducer:
    """Producer for publishing events to RabbitMQ."""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host=settings.RABBITMQ_VHOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare the exchange
            self.channel.exchange_declare(
                exchange=settings.RABBITMQ_EXCHANGE,
                exchange_type='topic',
                durable=True
            )
            
            logger.info("Successfully connected to RabbitMQ")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}", exc_info=True)
            raise
    
    def publish_event(self, routing_key: str, event_data: Dict[str, Any]):
        """
        Publish an event to RabbitMQ.
        
        Args:
            routing_key: Routing key for the message (e.g., 'document.authenticated')
            event_data: Event data dictionary to publish
        """
        try:
            if not self.connection or self.connection.is_closed:
                self._connect()
            
            # Convert event data to JSON
            message = json.dumps(event_data, default=str)
            
            # Publish message
            self.channel.basic_publish(
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json',
                )
            )
            
            logger.info(
                f"Published event to RabbitMQ - "
                f"routing_key: {routing_key}, data: {event_data}"
            )
            
        except Exception as e:
            logger.error(
                f"Failed to publish event - "
                f"routing_key: {routing_key}, error: {str(e)}",
                exc_info=True
            )
            raise
    
    def close(self):
        """Close the RabbitMQ connection."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {str(e)}", exc_info=True)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Singleton instance
_producer_instance = None


def get_rabbitmq_producer() -> RabbitMQProducer:
    """
    Get or create RabbitMQ producer singleton instance.
    
    Returns:
        RabbitMQProducer: Singleton producer instance
    """
    global _producer_instance
    
    if _producer_instance is None:
        _producer_instance = RabbitMQProducer()
    
    return _producer_instance
