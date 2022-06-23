import sqlite3
from typing import Dict, List, Tuple, Optional


class Db:
    # SqlScript for db creation if not exists
    def __init__(self, Connect: str, SqlScript: Optional[str]) -> None:
        self.conn = sqlite3.connect(Connect)
        self.cursor = self.conn.cursor()
        if SqlScript:
            with open(SqlScript, "r") as f:
                sql = f.read()
            self.cursor.executescript(sql)
            self.conn.commit()

    def insert_columns(self, table: str, columns: Dict) -> None:
        keys = ",".join(columns.keys())
        values = [tuple(columns.values())]
        placeholders = ",".join("?" * len(columns.keys()))
        self.conn.executemany(
            f"INSERT OR IGNORE INTO {table} "
            f"({keys})"
            f"({placeholders})",
            values
        )

    def get_cursor(self):
        return self.cursor

    def delete_row(self, table: str, row_id: int) -> None:
        row_id = int(row_id)
        self.cursor.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        self.conn.commit()
