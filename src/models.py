from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class User:
    id: str
    username: str
    password_hash: str  # SHA-256 of the raw password; never the plaintext


@dataclass
class Task:
    id: str
    user_id: str
    title: str
    description: str
    priority: Priority
    due_date: datetime | None = None
    completed: bool = False
    category: str = ""


@dataclass
class Reminder:
    id: str
    user_id: str
    task_id: str
    remind_at: datetime
    delivered: bool = False
