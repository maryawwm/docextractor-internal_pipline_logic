from typing import List
from uuid import UUID
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

from src.db.enums import DocumentStatusEnum, TaskStatusEnum

class ConfigMixin:
    model_config = {
        "from_attributes": True,
    }

class ChunkSchema(BaseModel, ConfigMixin):
    id: int
    document_id: UUID
    uid: UUID
    milvus_embedded: bool
    elastic_embedded: bool
    processed: bool
    created_at: datetime
    modified_at: datetime

class TaskSchema(BaseModel, ConfigMixin):
    id: int
    uid: UUID
    document_id: UUID
    callback_url: str
    payload: int
    status: TaskStatusEnum
    created_at: datetime
    modified_at: datetime

class DocumentSchema(BaseModel, ConfigMixin):
    id: int
    uid: UUID
    status: DocumentStatusEnum
    total_chunks: int
    complete_chunks: int
    processed_at: datetime
    created_at: datetime
    modified_at: datetime
    tasks: List[TaskSchema] = Field(default_factory=list)
    chunks: List[ChunkSchema] = Field(default_factory=list)
