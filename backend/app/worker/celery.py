# Celery configuration
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "5g-ticketing-worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.worker.tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_routes={
        "app.worker.tasks.process_ocr": {"queue": "ocr"},
        "app.worker.tasks.export_excel": {"queue": "export"},
        "app.worker.tasks.export_docx": {"queue": "export"},
    }
)