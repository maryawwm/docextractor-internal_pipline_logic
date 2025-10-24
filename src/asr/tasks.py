import os
import logging

from src.core.settings import app_settings
from src.core.worker import celery_worker
from src.db.crud import get_process_data_by_task_id, log_process_step, save_process_result
from src.utilities.aes_utility import decrypt
from src.utilities.minio_utility import MinioUtility
from src.asr.schemas import ASRPayload, MappingDataSchema
from src.asr.services import WhisperTurboService

logger = logging.getLogger(__name__)


@celery_worker.task
def asr_transcription_pipeline(req_task_id: int):
    log_process_step(task_id=req_task_id, log_type_id=1, calling_process="asr_transcription")
    task_data = get_process_data_by_task_id(task_id=req_task_id)
    if not task_data:
        return
    try:
        payload = ASRPayload.model_validate_json(task_data["ProcessPayload"])
        document_id = task_data["DocumentId"]

        input_minio_access_key = decrypt(payload.input_minio_cred.minio_access_key)
        input_minio_secret_key = decrypt(payload.input_minio_cred.minio_secret_key)

        input_minio = MinioUtility(
            access_key=input_minio_access_key,
            secret_key=input_minio_secret_key,
            endpoint=payload.input_minio_endpoint,
            secure=app_settings.minio_security,
        )

        os.makedirs(app_settings.document_path, exist_ok=True)
        file_extension = os.path.splitext(payload.input_object_path)[-1]
        audio_path = f"{app_settings.document_path}/{req_task_id}{file_extension}"

        log_process_step(task_id=req_task_id, log_type_id=2, calling_process="asr_transcription")
        input_minio.download_file(
            bucket_name=payload.input_bucket_name,
            file_key=payload.input_object_path,
            file_path=audio_path,
        )
        log_process_step(task_id=req_task_id, log_type_id=3, calling_process="asr_transcription")

        service = WhisperTurboService(
            api_key=getattr(app_settings, "openai_api_key", None),
            base_url=getattr(app_settings, "openai_base_url", None),
        )

        kwargs = {}
        if payload.language is not None:
            kwargs["language"] = payload.language
        if payload.temperature is not None:
            kwargs["temperature"] = payload.temperature
        if payload.prompt is not None:
            kwargs["prompt"] = payload.prompt

        result = service.transcribe(audio_path, **kwargs)

        # Save the full text
        log_process_step(task_id=req_task_id, log_type_id=6, calling_process="asr_transcription")
        save_process_result(
            task_id=req_task_id,
            document_id=document_id,
            content=result.get("text", ""),
            mapping_data=MappingDataSchema(type="txt").model_dump_json(),
        )

        # Save segments if present
        for idx, seg in enumerate(result.get("segments", []) or []):
            save_process_result(
                task_id=req_task_id,
                document_id=document_id,
                content=seg.get("text", ""),
                mapping_data=MappingDataSchema(
                    type="segment", segment_index=idx, start=seg.get("start"), end=seg.get("end")
                ).model_dump_json(),
            )

        # Optionally upload raw transcript to output MinIO if provided
        if payload.output_minio_cred and payload.output_bucket_name and payload.output_object_path:
            log_process_step(task_id=req_task_id, log_type_id=4, calling_process="asr_transcription")
            transcript_file = f"{app_settings.document_path}/{req_task_id}.txt"
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(result.get("text", ""))

            output_minio_access_key = decrypt(payload.output_minio_cred.minio_access_key)
            output_minio_secret_key = decrypt(payload.output_minio_cred.minio_secret_key)
            output_minio = MinioUtility(
                access_key=output_minio_access_key,
                secret_key=output_minio_secret_key,
                endpoint=payload.output_minio_endpoint,
                secure=app_settings.minio_security,
            )
            output_key = os.path.join(payload.output_object_path, f"{req_task_id}.txt")
            output_minio.upload_file(
                bucket_name=payload.output_bucket_name,
                file_key=output_key,
                file_path=transcript_file,
            )
            log_process_step(task_id=req_task_id, log_type_id=7, calling_process="asr_transcription")

        log_process_step(task_id=req_task_id, log_type_id=8, calling_process="asr_transcription")
    except Exception as e:
        logger.error(f"Error in asr_transcription task: {e}")
