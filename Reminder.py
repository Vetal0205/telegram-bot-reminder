import os
import re
import Exceptions
from db import Db
from Classes import Message, Task
from typing import List, Tuple, Optional, Dict

DataBase = Db(Connect=os.path.join("db", "telegram-bot-reminder.sqlite"), SqlScript="createDb.sql")


def add_task(date: str, time: str, task: str) -> Task:
    datetime = [date, time]
    DataBase.insert_columns(
        "Task",
        {
            "title": task,
            "task_date": date,
            "task_time": time
        }
    )
    return Task(id=None, date=date, time=time, task=task)


def del_task(row_id: str) -> None:
    row_id = re.match(r"^(/del)([\d]+)(.*)$", row_id)
    if not row_id.group(0) or not row_id.group(1) or not row_id.group(2):
        raise Exceptions.NotCorrectMessage("[!] Invalid syntax [!]")
    DataBase.delete_row(table="Task", row_id=row_id.group(2))


def get_all_tasks() -> List[Task]:
    rows = DataBase.fetch("Task", ["id", "title", "task_date", "task_time"])
    all_tasks = [Task(id=row[0], task=row[1], date=row[2], time=row[3]) for row in rows]
    return all_tasks

