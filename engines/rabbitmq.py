import pika
import os

from pika.adapters.blocking_connection import BlockingChannel
from typing import Any, Callable

host = os.environ.get("RABBITMQ_HOST", "localhost")
port = os.environ.get("RABBITMQ_PORT", "5672")
username = os.environ.get("RABBITMQ_USERNAME", "")
password = os.environ.get("RABBITMQ_PASSWORD", "")

class RabbitMQ:
    def __init__(self):
        connection_parameters = pika.ConnectionParameters(
            host=host, 
            port=port,
        )

        if username and password:
            connection_parameters.credentials = pika.PlainCredentials(
                username=username,
                password=password,
            )

        self.connection: pika.BlockingConnection = pika.BlockingConnection(connection_parameters)
        self.channel: BlockingChannel = self.connection.channel()

    def init_channel(self, *args, **kwargs):
        self.channel.queue_declare(*args, **kwargs)

    def publish(self, key: str, data: str):
        self.channel.basic_publish(exchange='', routing_key=key, body=data)

    def consume(self, key: str, callback: Callable[[Any, Any, Any, Any], None]):
        self.channel.basic_consume(queue=key, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

rabbitmq_client = RabbitMQ()

