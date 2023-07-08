from __future__ import annotations
from typing import Any

import sqlite3


class DateBase:
    def __init__(self, table_path: str):
        self.connection = sqlite3.connect(table_path)
        self.cursor = self.connection.cursor()

    def insert(self, table: str, column_values: dict) -> None:
        """Операция вставки в БД"""
        columns = ', '.join(column_values.keys())
        values = [tuple(column_values.values())]
        placeholders = ', '.join('?' * len(column_values.keys()))
        self.cursor.executemany(
            f"insert into {table}"
            f"({columns})"
            f"values ({placeholders});",
            values)
        self.connection.commit()

    def update_values(self, table: str, values: dict, params: dict) -> None:
        list_values = [f"{key} = ?" for key in values]
        set_where = [f"{key} = '{val}'" for key, val in params.items()]
        row = tuple(values.values())
        self.cursor.execute(f"""UPDATE {table} SET {', '.join(list_values)} WHERE {' AND '.join(set_where)};""", row)
        self.connection.commit()

    def get_cell_value(self, table: str, cell: str, finder_param: tuple) -> Any:
        """Get value one cell"""
        self.cursor.execute(f"SELECT {cell} FROM {table} WHERE {finder_param[0]} = ?", (finder_param[1],))
        return self.cursor.fetchone()[0]

    def get_column(self, table: str, name_column: str) -> tuple:
        """Get column"""
        self.cursor.execute(f"select {name_column} from {table}")
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            result.append(row[0])

        return tuple(result)

    def get_row(self, table: str, name_column: tuple[str], search_param: dict) -> dict:
        """Get row"""
        set_where = [f"{key} = ?" for key in search_param]
        row = tuple(search_param.values())
        self.cursor.execute(f"SELECT {', '.join(name_column)} FROM {table} WHERE {' AND '.join(set_where)}", row)
        rows = self.cursor.fetchall()
        dict_row = {}
        for row in rows:
            for index, column in enumerate(name_column):
                dict_row[column] = row[index]
        return dict_row

    def fetchall(self, table: str, columns: list[str]) -> list[dict]:
        """Операция извлечения данных из БД"""
        columns_joined = ', '.join(columns)
        self.cursor.execute(f"select {columns_joined} from {table}")
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            dict_row = {}
            for index, column in enumerate(columns):
                dict_row[column] = row[index]
            result.append(dict_row)
        return result

    def delete_values(self, table: str, row_id: int) -> None:
        """Операция удаления из БД"""
        row_id = int(row_id)
        self.cursor.execute(f"delete from {table} where id={row_id}")
        self.connection.commit()

    def get_cursor(self):
        return self.cursor

    def create_table(self, table: str, column: dict) -> None:
        columns = [' '.join(val) for val in column.items()]
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table}
                                (id INTEGER PRIMARY KEY, {", ".join(columns)});''')
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def delete_table(self, table: str) -> None:
        self.cursor.execute(f"DROP TABLE {table}")


DB_PATH = "db/db_bot.db"

table_name_chatgpt = "messages_chatgpt"
table_column_chatgpt = {"user_id": "INTEGER",
                        "messages": "TEXT",
                        "tokens": "INTEGER",
                        "max_tokens": "INTEGER"}

table_name_users = "users"
table_column_users = {"user_id": "INTEGER",
                      "tokens": "INTEGER",
                      "name": "TEXT",
                      "surname": "TEXT",
                      "age": "INTEGER",
                      "gender": "TEXT",
                      "wish_news": "INTEGER"}

with DateBase(DB_PATH) as db:
    db.create_table(table_name_chatgpt, table_column_chatgpt)
    db.create_table(table_name_users, table_column_users)
