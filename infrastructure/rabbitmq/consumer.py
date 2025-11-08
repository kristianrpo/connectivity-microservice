"""
RabbitMQ consumer for document authentication events.
"""

import json
import logging
import pika
from typing import Callable, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """
    RabbitMQ consumer for listening to document authentication events.
    """
    
    def __init__(
        self,
        queue_name: str,
        routing_key: str
    ):
        """
        Configure RabbitMQ consumer.

        Args:
            queue_name: Name of the queue to consume from
            routing_key: Routing key to listen to
        """
        self.host = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.username = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASSWORD
        self.vhost = settings.RABBITMQ_VHOST
        self.exchange = settings.RABBITMQ_EXCHANGE
        
        self.queue_name = queue_name
        self.routing_key = routing_key
        
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Establish connection to RabbitMQ."""
        credentials = pika.PlainCredentials(self.username, self.password)
        
        # Configure SSL for AWS MQ if using port 5671
        ssl_options = None
        if self.port == 5671:
            import ssl
            ssl_options = pika.SSLOptions(ssl.create_default_context())
        
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.vhost,
            credentials=credentials,
            ssl_options=ssl_options,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # Declare exchange (skip if using default exchange)
        if self.exchange:
            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='topic',
                durable=True
            )
        
        # Declare queue
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True
        )
        
        # Bind queue to exchange with routing key
        self.channel.queue_bind(
            exchange=self.exchange,
            queue=self.queue_name,
            routing_key=self.routing_key
        )
        
        logger.info(
            f"Connected to RabbitMQ. Queue: {self.queue_name}, "
            f"Routing key: {self.routing_key}"
        )
    
    def process_message(self, body: dict):
        """
        Override this method in subclasses to process messages.
        
        Args:
            body: Parsed message body as dict
        """
        raise NotImplementedError("Subclasses must implement process_message()")
    
    def on_message(self, ch, method, properties, body):
        """
        Callback for when a message is received.
        
        Args:
            ch: Channel
            method: Method frame
            properties: Message properties
            body: Message body (bytes)
        """
        try:
            # Parse message
            message = json.loads(body.decode('utf-8'))
            
            logger.info(f"Received message from queue {self.queue_name}")
            
            # Call subclass implementation
            self.process_message(message)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message JSON: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            # Reject and requeue (will retry)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages from the queue."""
        if not self.connection or not self.channel:
            self.connect()
        
        # Set QoS
        self.channel.basic_qos(prefetch_count=1)
        
        # Start consuming
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_message
        )
        
        logger.info(f"Starting to consume messages from queue: {self.queue_name}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop_consuming()
    
    def stop_consuming(self):
        """Stop consuming and close connection."""
        if self.channel:
            self.channel.stop_consuming()
        
        if self.connection:
            self.connection.close()
        
        logger.info("Stopped consuming messages")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_consuming()
