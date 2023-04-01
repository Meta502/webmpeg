import json
import logging
import ffmpeg

from django.core.management import django, os, sys
from engines.rabbitmq import rabbitmq_client

RABBITMQ_QUEUE_KEY = os.environ.get("RABBITMQ_QUEUE_KEY", "default")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

# Import Django models here
from media.models import Video
from workers.video_processor import VideoProcessor

def process_video(video: Video):
    input = ffmpeg.input(video.file.path)
    processed_stream = VideoProcessor.run(
        input,
        video.operation_group,
    ) 

    processed_stream.output(
        f"uploads/{video.id}.mp4",
        loglevel="quiet"
    ).overwrite_output().run()

    video.status = Video.MediaStatusType.FINISHED
    video.save()

def callback(ch, method, properties, body):
    try:
        parsed_body = json.loads(body) 
        video = Video.objects.filter(id=parsed_body["id"]).first()
        
        if not video:
            raise Exception("Video not found")

        process_video(video)
        print(f"[FINISHED PROCESSING] {video.filename}")
    except Exception as e:
        logging.error(e)

def main():
    print(" [*] Waiting for messages. To exit press CTRL+C")
    rabbitmq_client.consume(RABBITMQ_QUEUE_KEY, callback=callback)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(0)
