from django.contrib.auth.models import User
from django.core.management import os
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.fields.json import json
from django.urls.converters import uuid

from engines.rabbitmq import rabbitmq_client

# Create your models here.
class Video(models.Model):
    class MediaStatusType:
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        FINISHED = "finished"

    MEDIA_STATUS_TYPE_CHOICES = {
        MediaStatusType.PENDING: "Pending",
        MediaStatusType.IN_PROGRESS: "In Progress",
        MediaStatusType.FINISHED: "Finished",
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    file = models.FileField()

    status = models.CharField(
        max_length=64,
        choices=MEDIA_STATUS_TYPE_CHOICES.items(),
        default=MediaStatusType.PENDING,
    )

    quality_level = models.IntegerField(
        default=23,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(51),
        ]
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="videos")

    def start_processing(self):
        rabbitmq_client.publish("default", json.dumps({ "id": str(self.id) }))

    @property
    def processed_file(self):
        if self.status != self.MediaStatusType.FINISHED:
            return None

        return f"/uploads/{self.id}.{self.file_extension}"

    @property
    def file_extension(self):
        file_split = self.filename.split(".")
        if len(file_split) == 0:
            return ""

        if len(file_split) == 1:
            return file_split[0]

        return file_split[-1]

    @property
    def filename(self) -> str:
        return os.path.basename(self.file.name)

class OperationGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    video = models.OneToOneField(Video, related_name="operation_group", on_delete=models.CASCADE)

class Operation(models.Model):
    class MediaOperationType:
        CROP = "crop"
        TRIM = "trim"
        VFLIP = "vflip"
        HFLIP = "hflip"
        RESIZE = "resize"

    MEDIA_OPERATION_TYPE_CHOICES = {
        MediaOperationType.CROP: "Crop",
        MediaOperationType.TRIM: "Trim",
        MediaOperationType.VFLIP: "Vertical Flip",
        MediaOperationType.HFLIP: "Horizontal Flip",
        MediaOperationType.RESIZE: "Resize"
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    group = models.ForeignKey(OperationGroup, related_name="operations", on_delete=models.CASCADE)
    operation_name = models.CharField(choices=MEDIA_OPERATION_TYPE_CHOICES.items(), max_length=32)
    arguments = models.JSONField(blank=True, null=True)

