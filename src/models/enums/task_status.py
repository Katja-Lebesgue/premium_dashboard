import enum


class TaskStatus(enum.Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    SCHEDULED = "SCHEDULED"
