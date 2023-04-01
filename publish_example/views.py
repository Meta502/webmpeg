import json

from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import permissions

from engines.rabbitmq import rabbitmq_client

# Create your views here.
class PublishTaskView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        rabbitmq_client.publish(key="default", data=json.dumps(request.data))

        return Response("Check your worker log, request should be received there.")
