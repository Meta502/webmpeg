from django.core.management import django, os, sys
from engines.rabbitmq import rabbitmq_client

RABBITMQ_QUEUE_KEY = os.environ.get("RABBITMQ_QUEUE_KEY", "default")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

# Import Django models here

def callback(ch, method, properties, body):
    print(" [x] received %r" % body)

def main():
    client = rabbitmq_client

    print(" [*] Waiting for messages. To exit press CTRL+C")
    client.consume(RABBITMQ_QUEUE_KEY, callback=callback)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(0)
