from enum import Enum


class TransactionStatus(str, Enum):
    in_progress = "in_progress"
    pending = "pending"
    completed = "completed"
    faulted = "faulted"
