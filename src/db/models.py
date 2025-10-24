from sqlalchemy.dialects.mssql import DATETIMEOFFSET
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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
