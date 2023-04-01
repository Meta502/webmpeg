from django.db.models.fields.json import json
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import serializers
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from media.constants import VIDEO_CREATE_DEFAULT_OPERATIONS

from media.models import Operation, OperationGroup, Video

# Create your views here.
class ListCreateVideoView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    class CreateVideoRequestSerializer(serializers.Serializer):
        class OperationSerializer(serializers.Serializer):
            operation_name = serializers.ChoiceField(choices=[tuple(item) for item in Operation.MEDIA_OPERATION_TYPE_CHOICES.items()])
            arguments = serializers.JSONField()

        file = serializers.FileField()
        operations = serializers.ListSerializer(child=OperationSerializer())

    class CreateVideoResponseSerializer(serializers.Serializer):
        message = serializers.CharField()


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Video to be uploaded'),
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
        tags=["Video"],
    )
    def post(self, request):
        serializer = self.CreateVideoRequestSerializer(
            data={
                "file": request.data["file"],
                "operations": json.loads(request.data["operations"]),
            }
        )
        serializer.is_valid(raise_exception=True)
        
        video = Video.objects.create(
            file=serializer.validated_data["file"],
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
        
