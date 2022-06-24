import os
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
            "task_time": " ".join(datetime)
        }
    )
    return Task(id=None, datatime=" ".join(datetime), task=task)


def del_task(row_id: int) -> None:
    DataBase.delete_row(table="Task", row_id=row_id)


def get_all_tasks() -> List[Task]:
    cursor = DataBase.get_cursor()
    cursor.execute("SELECT * FROM Task ORDERED BY task_time ASC")
    rows = cursor.fetchall()
    all_tasks = [Task(id=row[0], task=row[1], datatime=row[2]) for row in rows]
    return all_tasks
