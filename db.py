import sqlite3
from typing import Dict, List, Tuple, Optional
from Exceptions import NoSQLSequence


class Db:
    # SqlScript for db creation if not exists
    def __init__(self, Connect: str, SqlScript: Optional[str]):
        self.conn = sqlite3.connect(Connect)
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master "
                            "WHERE type='table' AND name='Task'")
        table_exists = self.cursor.fetchall()
        if not table_exists:
            try:
                self._init_db(SqlScript)
            except NoSQLSequence():
                pass

    def _init_db(self, SqlScript: str) -> None:
        with open(SqlScript, "r") as f:
            sql = f.read()
        self.cursor.executescript(sql)
        self.conn.commit()

    def insert_columns(self, table: str, columns: Dict) -> None:
        keys = ",".join(columns.keys())
        values = [tuple(columns.values())]
        placeholders = ",".join("?" * len(columns.keys()))
        self.conn.executemany(
            f"INSERT INTO {table} ({keys}) VALUES ({placeholders})", values)
        self.conn.commit()

    def get_cursor(self):
        return self.cursor

    def delete_row(self, table: str, row_id: int) -> None:
        row_id = int(row_id)
        self.cursor.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        self.cursor.execute(f"DELETE FROM sqlite_sequence WHERE seq = ?", (row_id,))
        self.conn.commit()

    def fetch(self, table: str, columns: List[str]) -> List:
        columns_joined = ", ".join(columns)
        self.cursor.execute(f"SELECT {columns_joined} FROM {table}")
        rows = self.cursor.fetchall()
        return rows
