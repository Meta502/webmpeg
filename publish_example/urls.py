from publish_example.views import PublishTaskView
from django.urls import path

urlpatterns = [
    path("publish", PublishTaskView.as_view(), name="publish-example")
]
