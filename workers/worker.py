import json
import logging
from threading import Thread
from typing import List
from django.utils.autoreload import threading
import ffmpeg

from django.core.management import django, functools, os, sys
from pika import BlockingConnection
from pika.spec import Channel
from engines.rabbitmq import rabbitmq_client

RABBITMQ_QUEUE_KEY = os.environ.get("RABBITMQ_QUEUE_KEY", "default")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

# Import Django models here
from media.models import Video
from workers.video_processor import VideoProcessor

def ack_message(channel, delivery_tag, is_nack=False):
    """Note that `channel` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if channel.is_open:
        if not is_nack:
            channel.basic_ack(delivery_tag)
        else:
            channel.basic_nack(delivery_tag)
    else:
        # Channel is already closed, so we can't ACK this message;
        # log and/or do something that makes sense for your app in this case.
        pass

def process_video(video: Video, connection: BlockingConnection, channel: Channel, delivery_tag):
    input = ffmpeg.input(video.file.path)

    processed_audio, processed_video = VideoProcessor.run(
        input.audio,
        input.video,
        video.operation_group,
    ) 

    try:
        ffmpeg.output(
            processed_video,
            processed_audio,
            f"uploads/{video.id}.mp4",
            threads=2
        ).overwrite_output().run()
    except ffmpeg.Error as e:
        cb = functools.partial(ack_message, channel=channel, delivery_tag=delivery_tag, is_nack=True)
        connection.add_callback_threadsafe(cb)
        print(f"[REQUEST FAILED] {video.id}")
        return

    video.status = Video.MediaStatusType.FINISHED
    video.save()

    cb = functools.partial(ack_message, channel=channel, delivery_tag=delivery_tag, is_nack=False)
    connection.add_callback_threadsafe(cb)
    print(f"[FINISHED REQUEST] {video.id}")

def on_message(ch, method, properties, body, args):
    connection, threads = args
    try:
        parsed_body = json.loads(body) 
        video = Video.objects.filter(id=parsed_body["id"]).first()

        if not video:
            raise Exception("Video not found")

        print(f"[RECEIVED REQUEST] {video.id}")
        delivery_tag = method.delivery_tag
        thread = threading.Thread(target=process_video, args=(video, connection, ch, delivery_tag))
        thread.start()
        threads.append(thread)
    except Exception as e:
        logging.error(e)

def main(threads: List[Thread]):
    print(" [*] Waiting for messages. To exit press CTRL+C")
    on_message_callback = functools.partial(on_message, args=(rabbitmq_client.connection, threads))    

    rabbitmq_client.consume(RABBITMQ_QUEUE_KEY, callback=on_message_callback)

if __name__ == "__main__":
    threads = []
    try:
        main(threads)
    except KeyboardInterrupt:
        print("Interrupted")

        for thread in threads:
            thread.join()

        try:
            sys.exit(1)
        except SystemExit:
            os._exit(0)
