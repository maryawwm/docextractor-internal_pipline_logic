from celery import Celery
from src.core.settings import app_settings
from src.app_logger.manager import setup_logging

setup_logging()

celery_worker = Celery(
    "worker",
    backend=app_settings.celery_backend,
    broker=app_settings.celery_broker,
    include=["src.normal_document.tasks"],
)
celery_worker.conf.update(
    broker_connection_retry_on_startup=True,
    worker_hijack_root_logger=False,
)