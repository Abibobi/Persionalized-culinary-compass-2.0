from django.urls import path
from .views import health_check, queue_ping, task_status

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("tasks/ping/", queue_ping, name="queue-ping"),
    path("tasks/<str:task_id>/", task_status, name="task-status"),
]