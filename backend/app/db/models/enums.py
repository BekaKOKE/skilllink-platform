from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    specialist = "specialist"
    client = "client"
    regulator = "regulator"


class OrderStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class EventStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"