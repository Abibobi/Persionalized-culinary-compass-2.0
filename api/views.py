from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from celery.result import AsyncResult

from .tasks import ping_task


@extend_schema(tags=["Health"], summary="Health check")
@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok", "service": "pcc-api", "version": "v1"})


@extend_schema(tags=["Health"], summary="Queue async ping task")
@api_view(["POST"])
def queue_ping(request):
    name = request.data.get("name", "chef")
    task = ping_task.delay(name)
    return Response({"task_id": task.id, "status": "queued"}, status=202)


@extend_schema(tags=["Health"], summary="Get async task status/result")
@api_view(["GET"])
def task_status(request, task_id):
    task_result = AsyncResult(task_id)
    payload = {
        "task_id": task_id,
        "state": task_result.state,
    }
    if task_result.ready():
        payload["result"] = task_result.result
    return Response(payload)