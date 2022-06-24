CREATE TABLE Task (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title  TEXT UNIQUE,
    task_date TEXT,
    task_time TEXT
);
