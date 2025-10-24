import uuid
from enum import Enum

from datetime import datetime

from sqlalchemy.dialects.mssql import DATETIMEOFFSET
from sqlalchemy.dialects.mssql.base import UNIQUEIDENTIFIER
from sqlalchemy import (
    BigInteger,
    CHAR,
    NCHAR,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Enum as SQLEnum
)
from sqlalchemy.dialects.mysql.types import CHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.db.enums import TaskStatusEnum, DocumentStatusEnum
from src.utilities.datetime.utc_datetime import utc_now


class Base(DeclarativeBase):
    pass


class ProcessLogs(Base):
    __tablename__ = "process_logs"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True)
    TaskId: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("process_requests.TaskId"), index=True
    )
    LogTypeId: Mapped[int] = mapped_column(Integer, ForeignKey("process_type.Id"))
    StartTime: Mapped[DateTime] = mapped_column(DateTime)

    request: Mapped["ProcessRequests"] = relationship(
        "ProcessRequests", back_populates="logs"
    )
    log_type: Mapped["ProcessType"] = relationship("ProcessType", back_populates="logs")


class ProcessRequests(Base):
    __tablename__ = "process_requests"

    Id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    TaskId: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    UserId: Mapped[int] = mapped_column(BigInteger)
    DocumentId: Mapped[int] = mapped_column(BigInteger)
    EndpointName: Mapped[str] = mapped_column(String)
    ProcessPayload: Mapped[str] = mapped_column(String)
    StartTime: Mapped[DATETIMEOFFSET] = mapped_column(DATETIMEOFFSET)
    EndTime: Mapped[DATETIMEOFFSET | None] = mapped_column(
        DATETIMEOFFSET, nullable=True
    )

    logs: Mapped[list["ProcessLogs"]] = relationship(
        "ProcessLogs", back_populates="request", cascade="all, delete-orphan"
    )
    results: Mapped[list["ProcessResult"]] = relationship(
        "ProcessResult", back_populates="request", cascade="all, delete-orphan"
    )


class ProcessResult(Base):
    __tablename__ = "process_result"

    Id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    TaskId: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("process_requests.TaskId"), index=True
    )
    DocumentId: Mapped[int] = mapped_column(Integer)
    Content: Mapped[str] = mapped_column(String)
    CreatedAt: Mapped[DATETIMEOFFSET] = mapped_column(DATETIMEOFFSET)
    MappingData: Mapped[str] = mapped_column(String)

    request: Mapped["ProcessRequests"] = relationship(
        "ProcessRequests", back_populates="results"
    )


class ProcessType(Base):
    __tablename__ = "process_type"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True)
    Title: Mapped[str] = mapped_column(String, nullable=False)

    logs: Mapped[list["ProcessLogs"]] = relationship(
        "ProcessLogs", back_populates="log_type"
    )
class Document(Base):
    __tablename__ = "document"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    uid: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        unique=True,
        index=True,
    )
    status: Mapped[DocumentStatusEnum] = mapped_column(
        SQLEnum(DocumentStatusEnum, native_enum=False, length=50),
        nullable=False,
        default=DocumentStatusEnum.STARTED,
    )
    total_chunks: Mapped[int] = mapped_column(BigInteger, nullable=False)
    complete_chunks: Mapped[int] = mapped_column(BigInteger, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="document", cascade="all, delete-orphan"
    )
    chunks: Mapped[list["Chunk"]] = relationship(
        "Chunk", back_populates="document", cascade="all, delete-orphan"
    )
class Task(Base):

    __tablename__ = "task"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    uid: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        unique=True,
        index=True,
        nullable=False
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("document.uid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    callback_url: Mapped[str] = mapped_column(NCHAR(255), nullable=False)
    payload: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[TaskStatusEnum] = mapped_column(
        SQLEnum(TaskStatusEnum, native_enum=False, length=50),
        nullable=False,
        default=TaskStatusEnum.RECEIVED,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="tasks")

    __table_args__ = (
        Index("task_id_uid_document_id_index", "id", "uid", "document_id"),
    )


class Chunk(Base):
    __tablename__ = "chunk"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    document_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("document.uid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    uid: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        unique=True,
        index=True,
        nullable=False
    )

    milvus_embedded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    elastic_embedded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("chunk_id_document_id_index", "id", "document_id"),
    )
