from fastapi import APIRouter

from src.core.worker import celery_worker

router = APIRouter(tags=["force stop"])


@router.post("/force_stop")
def force_stop_by_task_id(task_id: int):
    celery_worker.control.revoke(str(task_id), terminate=True, signal="SIGKILL")
    return f"task: {task_id} stopped."
