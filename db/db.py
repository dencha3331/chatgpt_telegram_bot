import sqlite3
from logs import logger


class DateBase:
    def __init__(self, table_path: str):
        self.connection = sqlite3.connect(table_path)
        self.cursor = self.connection.cursor()

    def insert(self, table: str, column_values: dict):
        """Операция вставки в БД"""
        columns = ', '.join(column_values.keys())
        values = [tuple(column_values.values())]
        placeholders = ', '.join('?' * len(column_values.keys()))
        self.cursor.executemany(
            f"insert into {table}"
            f"({columns})"
            f"values ({placeholders})",
            values)
        self.connection.commit()

    def _update_value(self, table: str, values: dict, params: dict):
        """Update value in one cell"""
        list_value = [f'{key} = "{val}"' for key, val in values.items()]
        set_where = [f"? = '{val}'" for val in params.values()]
        self.cursor.execute(f"""UPDATE {table} SET {", ".join(list_value)}
                                WHERE {' AND '.join(set_where)};""", tuple(params.keys()))
        # print((f"""UPDATE {table} SET {", ".join(list_value)}
        #                         WHERE {' AND '.join(set_where)};""", tuple(params.keys())))
        self.connection.commit()

    def update_values(self, table: str, values: dict, params: dict):
        list_values = [f"{key} = ?" for key in values]
        set_where = [f"{key} = '{val}'" for key, val in params.items()]
        row = tuple(values.values())
        # print(f"""UPDATE {table} SET {', '.join(list_values)} WHERE {' AND '.join(set_where)};""" )
        self.cursor.execute(f"""UPDATE {table} SET {', '.join(list_values)} WHERE {' AND '.join(set_where)};""", row)
        self.connection.commit()

    def get_cell_value(self, table: str, cell: str, finder_param: tuple):
        """Get value one cell"""
        self.cursor.execute(f"SELECT {cell} FROM {table} WHERE {finder_param[0]} = ?", (finder_param[1],))
        return self.cursor.fetchone()[0]

    def get_column(self, table: str, name_column: str):
        """Get column"""
        self.cursor.execute(f"select {name_column} from {table}")
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            result.append(row[0])

        return tuple(result)

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

    def create_db(self, table: str, column: dict):
        self.cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table}';''')
        if self.cursor.fetchone()[0] == 1:
            logger.debug('Таблица уже существует.')
        else:
            columns = [' '.join(val) for val in column.items()]
            self.cursor.execute(f'''CREATE TABLE {table}
                                    (id INTEGER PRIMARY KEY, {", ".join(columns)});''')
            self.connection.commit()

    def select_table(self):
        self.cursor.execute("""SELECT * FROM messages_chatgpt;""")
        return self.cursor.fetchall()

    def delete_table(self, table: str):
        self.cursor.execute(f"DROP TABLE {table}")

    def notification_tokens(self, count):
        """Notification user about count tokens if tokens < 40000 and mine"""
        pass


