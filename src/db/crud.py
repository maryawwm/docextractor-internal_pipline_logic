import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.db.manager import sessionmanager
from src.db.models import ProcessLogs, ProcessRequests, ProcessResult

logger = logging.getLogger(__name__)


def get_process_data_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
    """Safely fetch process data without returning detached ORM objects."""
    with sessionmanager.session() as session:
        stmt = select(
            ProcessRequests.ProcessPayload, ProcessRequests.DocumentId
        ).filter_by(TaskId=task_id)
        row = session.execute(stmt).one_or_none()

        if row is None:
            return None

        return {"ProcessPayload": row.ProcessPayload, "DocumentId": row.DocumentId}


def log_process_step(task_id: int, log_type_id: int, calling_process: str) -> Optional[int]:
    try:
        with sessionmanager.session() as session:
            with session.begin():
                new_log = ProcessLogs(
                    TaskId=task_id,
                    LogTypeId=log_type_id,
                    StartTime=datetime.now().astimezone(),
                )
                session.add(new_log)
            log_id = new_log.Id
        return log_id
    except SQLAlchemyError:
        logger.Info(f"{calling_process}: task_id{task_id}-{log_type_id}")


def save_process_result(task_id: int, document_id: int, content: str, mapping_data: Dict[str, Any]) -> Optional[int]:
    """Insert a process result and return its generated ID safely."""
    try:
        with sessionmanager.session() as session:
            with session.begin():
                new_result = ProcessResult(
                    TaskId=task_id,
                    DocumentId=document_id,
                    Content=content,
                    CreatedAt=datetime.now().astimezone(),
                    MappingData=mapping_data,
                )
                session.add(new_result)
            result_id = new_result.Id
        return result_id

    except SQLAlchemyError:
        # TODO: replace with proper logging
        return None
