from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from authentication.views import RegisterUserView

urlpatterns = [
    path("login/", obtain_auth_token, name="authentication-login"),
    path("register/", RegisterUserView.as_view(), name="authentication-register")
]
