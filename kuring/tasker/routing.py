from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tasker/(?P<task_id>\w+)/$', consumers.Tasker),
]
