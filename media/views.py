from django.db.models.fields.json import json
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import serializers
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from media.constants import VIDEO_CREATE_DEFAULT_OPERATIONS

from media.models import Operation, OperationGroup, Video


class OperationSerializer(serializers.Serializer):
    operation_name = serializers.ChoiceField(choices=[tuple(item) for item in Operation.MEDIA_OPERATION_TYPE_CHOICES.items()])
    arguments = serializers.JSONField()

class VideoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    file = serializers.FileField()
    operations = serializers.ListSerializer(child=OperationSerializer())
    status = serializers.CharField()
    processed_url = serializers.CharField(allow_blank=True, allow_null=True)

class ListCreateVideoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    class CreateVideoRequestSerializer(serializers.Serializer):    
        file = serializers.FileField()
        quality_level = serializers.IntegerField()
        operations = serializers.ListSerializer(child=OperationSerializer())

    class CreateVideoResponseSerializer(serializers.Serializer):
        message = serializers.CharField()

    class ListVideoResponseSerializer(serializers.Serializer): 
        videos = serializers.ListSerializer(child=VideoSerializer())

    @swagger_auto_schema(
        responses={
            "200": ListVideoResponseSerializer(),
        },
        tags=["video"],
    )
    def get(self, request):
        user_videos = {
            "videos": [
                {
                    "id": video.id,
                    "file": video.file,
                    "operations": video.operation_group.operations.all(),
                    "status": video.status,
                    "processed_url": video.processed_file,
                }
                for video in Video.objects.filter(user=request.user)
            ]
        } 

        return Response(
            self.ListVideoResponseSerializer(
                user_videos,
            ).data
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Video to be uploaded'),
            openapi.Parameter(
                'quality_level', 
                openapi.IN_FORM, 
                type=openapi.TYPE_NUMBER, 
                description="Quality of exported video (0 = highest, 51 = lowest)",
                default=23
            ),
            openapi.Parameter(
                'operations', 
                openapi.IN_FORM, 
                type=openapi.TYPE_OBJECT, 
                description='Operations to apply',
                default=json.dumps(VIDEO_CREATE_DEFAULT_OPERATIONS, indent=4)
            )
        ],
        responses={
            "201": CreateVideoResponseSerializer(),
        },
        tags=["video"],
    )
    def post(self, request):
        serializer = self.CreateVideoRequestSerializer(
            data={
                "file": request.data["file"],
                "quality_level": request.data["quality_level"],
                "operations": json.loads(request.data["operations"]),
            }
        )
        serializer.is_valid(raise_exception=True)
        
        video = Video.objects.create(
            file=serializer.validated_data["file"],
            quality_level=serializer.validated_data["quality_level"],
            user=request.user,
        )
        operation_group = OperationGroup.objects.create(
            video=video,
        )

        for operation in serializer.validated_data["operations"]:
            Operation.objects.create(
                group=operation_group,
                operation_name=operation["operation_name"],
                arguments=operation["arguments"],
            )

        video.start_processing()
        return Response(
            self.CreateVideoResponseSerializer(
                dict(
                    message="Upload successful, processing your video."
                )
            ).data,
            status=status.HTTP_201_CREATED
        )
        
