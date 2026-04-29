from celery import shared_task
import time


@shared_task
def ping_task(name="chef"):
    time.sleep(2)  # simulate async work
    return {"message": f"pong from celery, {name}!"}