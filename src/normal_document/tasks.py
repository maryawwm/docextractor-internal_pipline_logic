import logging
import os

from src.core.settings import app_settings
from src.core.worker import celery_worker
from src.db.crud import (
    get_process_data_by_task_id,
    log_process_step,
    save_process_result,
)
from src.normal_document.schemas import MappingDataSchema, ProcessPayload
from src.normal_document.services import NormalDocumentService
from src.utilities.aes_utility import decrypt
from src.utilities.minio_utility import MinioUtility

logger = logging.getLogger(__name__)


@celery_worker.task
def normal_document_extraction_pipeline(
    req_task_id: int,
):
    # TODO: try except
    log_process_step(
        task_id=req_task_id, log_type_id=1, calling_process="normal_document_extraction"
    )
    task_data = get_process_data_by_task_id(task_id=req_task_id)
    if task_data:
        try:
            payload = ProcessPayload.model_validate_json(task_data["ProcessPayload"])
            document_id = task_data["DocumentId"]

            input_minio_access_key = decrypt(payload.input_minio_cred.minio_access_key)
            input_minio_secret_key = decrypt(payload.input_minio_cred.minio_secret_key)

            input_minio = MinioUtility(
                access_key=input_minio_access_key,
                secret_key=input_minio_secret_key,
                endpoint=payload.input_minio_endpoint,
                secure=app_settings.minio_security,
            )
            documents_path = app_settings.document_path

            os.makedirs(documents_path, exist_ok=True)
            file_extension = os.path.splitext(payload.input_object_path)[-1]
            document_name = f"{documents_path}/{req_task_id}{file_extension}"

            log_process_step(
                task_id=req_task_id,
                log_type_id=2,
                calling_process="normal_document_extraction",
            )
            input_minio.download_file(
                bucket_name=payload.input_bucket_name,
                file_key=payload.input_object_path,
                file_path=document_name,
            )
            log_process_step(
                task_id=req_task_id,
                log_type_id=3,
                calling_process="normal_document_extraction",
            )
            logger.Info(f"Normal PDF Parse File. task_id{req_task_id}")
            document_service = NormalDocumentService(
                task_id=req_task_id, pages=payload.pages
            )
            document_service.convert(document_name)
            document_service.extract_page_by_page_md()

            for page_num, page_content in document_service.page_by_page_md.items():
                log_process_step(
                    task_id=req_task_id,
                    log_type_id=6,
                    calling_process="normal_document_extraction",
                )
                save_process_result(
                    task_id=req_task_id,
                    document_id=document_id,
                    content=page_content,
                    mapping_data=MappingDataSchema(
                        type="txt", page_number=page_num
                    ).model_dump_json(),
                )

            if payload.extract_images == 1:
                log_process_step(
                    task_id=req_task_id,
                    log_type_id=4,
                    calling_process="normal_document_extraction",
                )
                document_service.extract_pictures()
                output_minio_access_key = decrypt(
                    payload.output_minio_cred.minio_access_key
                )
                output_minio_secret_key = decrypt(
                    payload.output_minio_cred.minio_secret_key
                )

                output_minio = MinioUtility(
                    access_key=output_minio_access_key,
                    secret_key=output_minio_secret_key,
                    endpoint=payload.output_minio_endpoint,
                    secure=app_settings.minio_security,
                )

                for page_num, img_list in document_service.pics.items():
                    for idx, img in enumerate(img_list):
                        log_process_step(
                            task_id=req_task_id,
                            log_type_id=5,
                            calling_process="normal_document_extraction",
                        )
                        minio_img_path = output_minio.upload_file(
                            bucket_name=payload.output_bucket_name,
                            file_key=os.path.join(
                                payload.output_object_path, img.split("/")[-1]
                            ),
                            file_path=img,
                        )
                        log_process_step(
                            task_id=req_task_id,
                            log_type_id=7,
                            calling_process="normal_document_extraction",
                        )
                        save_process_result(
                            task_id=req_task_id,
                            document_id=document_id,
                            content=minio_img_path,
                            mapping_data=MappingDataSchema(
                                type="img", page_number=page_num, pic_number=idx + 1
                            ).model_dump_json(),
                        )
            log_process_step(task_id=req_task_id, log_type_id=8)
        except Exception as e:
            logger.error(f"Error In normal_document task:{e}")
    else:
        # TODO: callback, cleanup(doc and pictures)
        pass
