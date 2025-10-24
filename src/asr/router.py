from fastapi import APIRouter, status

from src.asr.tasks import asr_transcription_pipeline

router = APIRouter(tags=["asr transcription"])


@router.post("/asr", status_code=status.HTTP_202_ACCEPTED)
async def asr_transcription(req_task_id: int):
    asr_transcription_pipeline.apply_async(args=(req_task_id,), task_id=str(req_task_id))
    return f"task: {req_task_id} started."
