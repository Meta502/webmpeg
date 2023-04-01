from engines.rabbitmq import rabbitmq_client

RABBITMQ_QUEUES = {
    "default": {
        "queue": "default",
        "durable": True,
    }
}

def init_task_queues():
    for configuration in RABBITMQ_QUEUES.values():
        rabbitmq_client.init_channel(**configuration)

