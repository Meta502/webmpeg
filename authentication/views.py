from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from drf_yasg.utils import APIView, serializers, status, swagger_auto_schema
from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework.response import Response

class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    class RegisterUserRequestSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField()
        email = serializers.CharField()

    class RegisterUserResponseSerializer(serializers.Serializer):
        username = serializers.CharField()
        email = serializers.CharField()

    @swagger_auto_schema(
        request_body=RegisterUserRequestSerializer(),
        responses={
            "201": RegisterUserResponseSerializer(),
        }
    )
    def post(self, request):
        serializer = self.RegisterUserRequestSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
       
        user = authenticate(username=serializer.data["username"], password=serializer.data["password"])

        if user:
            raise APIException("User already exists")

        user = User.objects.create_user(
            username=serializer.data["username"],
            password=serializer.data["password"],
            email=serializer.data["email"],
        )

        return Response(
            self.RegisterUserResponseSerializer(
                user,
            ).data,
            status=status.HTTP_201_CREATED,
        )

