from fastapi import APIRouter, status

from src.normal_document.tasks import normal_document_extraction_pipeline

router = APIRouter(tags=["normal document extraction"])


@router.post("/normal_pdf", status_code=status.HTTP_202_ACCEPTED)
# TODO: basemodel for req_task_id
async def normal_document_extraction(req_task_id: int):
    normal_document_extraction_pipeline.apply_async(
        args=(req_task_id,), task_id=str(req_task_id)
    )
    # TODO: response schema
    return f"task: {req_task_id} started."
