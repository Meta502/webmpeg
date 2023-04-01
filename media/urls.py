from django.urls import path

from media.views import ListCreateVideoView

urlpatterns = [ 
    path("video/", ListCreateVideoView.as_view(), name="list-create-video-api")
]
