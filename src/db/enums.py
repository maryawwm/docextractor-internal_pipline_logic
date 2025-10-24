from enum import Enum

class TaskStatusEnum(str, Enum):
    RECEIVED = "received"
    PENDING = "pending"
    STARTED = "started"
    SEND_CALLBACK = "send_callback"
    DONE = "done"
    FAILED = "failed"

class DocumentStatusEnum(str, Enum):
    STARTED = "started"
    DONE = "done"
    FAILED = "failed"