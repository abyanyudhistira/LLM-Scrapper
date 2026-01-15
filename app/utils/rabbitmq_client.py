"""
RabbitMQ Client for queue operations
"""

import pika
import json
import logging
from typing import Dict, Callable
from app.utils.config import (
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, 
    RABBITMQ_PASSWORD, RABBITMQ_QUEUE, RABBITMQ_EXCHANGE,
    RABBITMQ_ROUTING_KEY
)

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """Client for RabbitMQ operations"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=RABBITMQ_EXCHANGE,
                exchange_type='direct',
                durable=True
            )
            
            # Declare queue
            self.channel.queue_declare(
                queue=RABBITMQ_QUEUE,
                durable=True
            )
            
            # Bind queue to exchange
            self.channel.queue_bind(
                exchange=RABBITMQ_EXCHANGE,
                queue=RABBITMQ_QUEUE,
                routing_key=RABBITMQ_ROUTING_KEY
            )
            
            # Set QoS - process one message at a time
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"Connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def publish(self, message: Dict):
        """Publish message to queue"""
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()
            
            self.channel.basic_publish(
                exchange=RABBITMQ_EXCHANGE,
                routing_key=RABBITMQ_ROUTING_KEY,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published message: {message.get('profile_id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise
    
    def consume(self, callback: Callable):
        """
        Start consuming messages from queue
        
        Args:
            callback: Function to process each message
                     Should accept (ch, method, properties, body)
        """
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()
            
            self.channel.basic_consume(
                queue=RABBITMQ_QUEUE,
                on_message_callback=callback,
                auto_ack=False  # Manual acknowledgment
            )
            
            logger.info(f"Started consuming from queue: {RABBITMQ_QUEUE}")
            logger.info("Waiting for messages. Press CTRL+C to exit.")
            
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in consumer: {e}")
            raise
    
    def stop(self):
        """Stop consuming and close connection"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.stop_consuming()
            
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            
            logger.info("RabbitMQ connection closed")
            
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    def get_queue_size(self) -> int:
        """Get number of messages in queue"""
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()
            
            method = self.channel.queue_declare(
                queue=RABBITMQ_QUEUE,
                durable=True,
                passive=True  # Don't create, just check
            )
            
            return method.method.message_count
            
        except Exception as e:
            logger.error(f"Error getting queue size: {e}")
            return 0


# Singleton instance
_rabbitmq_client = None

def get_rabbitmq_client() -> RabbitMQClient:
    """Get singleton RabbitMQ client instance"""
    global _rabbitmq_client
    if _rabbitmq_client is None:
        _rabbitmq_client = RabbitMQClient()
    return _rabbitmq_client
