from typing import NamedTuple, Optional


# Parsed message structure
class Message(NamedTuple):
    datatime: str
    task: str


# Db insert message structure
class Task(NamedTuple):
    id: Optional[int]
    date: str
    time: str
    task: str
