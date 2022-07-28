import contextlib
import os
import psycopg2

from exceptions import NotFound
from itertools import chain
from random import choice


class MediaTable:
    @staticmethod
    def get_columns():
        return [
            "id",
            "url",
            "author",
            "category",
            "nsfw",
            "has_been_sent",
            "submitted_by",
            "submitted_on",
        ]


class CategoryTable:
    @staticmethod
    def get_columns():
        return [
            "id",
            "name",
            "created_by",
            "created_on",
        ]


class Postgres:
    def __init__(
            self,
            database=os.environ.get("IZSAK_DB"),
            host=os.environ.get("IZSAK_DB_HOST"),
            user=os.environ.get("IZSAK_DB_USER"),
            password=os.environ.get("IZSAK_DB_PASS"),
            port=os.environ.get("IZSAK_DB_PORT"),
    ):
        self.conn = None
        self.cur = None
        self.database = database
        self.host = host
        self.user = user
        self.password = password
        self.port = port

    def _table_cols_lookup(self, table):
        if table == "media":
            return MediaTable.get_columns()
        elif table == "category":
            return CategoryTable.get_columns()

    def _execute(self, cmd, data=[], commit=True):
        self.cur.execute(cmd, data)
        if commit:
            self._commit()

    def _fetchone(self):
        try:
            return self.cur.fetchone()
        except psycopg2.ProgrammingError as e:
            if "no results to fetch" in str(e):
                return None

            raise e

    def _fetchall(self):
        try:
            return self.cur.fetchall()
        except psycopg2.ProgrammingError as e:
            if "no results to fetch" in str(e):
                return None

            raise e

    def _commit(self):
        self.conn.commit()

    def _create_dict(self, cols, vals):
        mapped_vals = dict()
        for i in range(len(cols)):
            mapped_vals[cols[i]] = vals[i]

        return mapped_vals

    def disconnect(self):
        self.cur.close()
        self.conn.close()
    
    def connect(self):
        self.conn = psycopg2.connect(
            database=self.database,
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
        )
        self.cur = self.conn.cursor()

    def get_row_count(self, table, where=None):
        stmt = f"SELECT count(*) FROM {table}"
        if where:
            stmt = f"{stmt} WHERE {where}"
        self._execute(stmt)
        return self._fetchone()

    def _format_insert(self, vals):
        formatted_rows = []
        for row in vals:
            row = ', '.join(list(map(lambda x: '%s', row)))
            formatted_rows.append(f"({row})")
        return formatted_rows

    def insert(self, table, cols, vals):
        formatters = ', '.join(self._format_insert(vals))
        stmt = f"INSERT INTO {table} ({', '.join(cols)}) VALUES {formatters};"
        self._execute(stmt, list(chain(*vals)))
        return self._fetchone()

    def update_field(self, table, field_name, new_val, id):
        stmt = f"UPDATE {table} SET {field_name} = %s WHERE id = %s;"
        self._execute(stmt, [new_val, id])
        return self.get_by_id(table, id)

    def select(self, table, where):
        stmt = f"SELECT * FROM {table} WHERE {where}"
        self._execute(stmt)
        item = self._fetchone()

        if item is None:
            raise NotFound("item with where clause: %s not found" % where)

        return self._create_dict(
            self._table_cols_lookup(table),
            list(item),
        )

    def del_by_id(self, table, id):
        stmt = f"DELETE FROM {table} WHERE id = %s;"
        self._execute(stmt, [id])
        return self._fetchone()

    def get_by_id(self, table, id):
        stmt = f"SELECT * FROM {table} WHERE id = %s;"
        self._execute(stmt, [id])
        item = self._fetchone()

        if item is None:
            raise NotFound("item with id %s not found" % id)

        return self._create_dict(
            self._table_cols_lookup(table),
            list(item),
        )

    def get_all_by_attr(self, table, attr, val):
        stmt = f"SELECT * FROM {table} WHERE {attr} = %s;"
        self._execute(stmt, [val])
        items = self._fetchall()
        if items is None:
            raise NotFound(f"no items matching {attr} = {val}")

        return [
            self._create_dict(
                self._table_cols_lookup(table),
                item,
            ) for item in items
        ]

    def get_all_by_category(self, category):
        stmt = "SELECT * FROM mediaV2 WHERE %s = ANY (category);"
        self._execute(stmt, [category])
        items = self._fetchall()
        if items is None:
            raise NotFound(f"no items in category {category}")

        return [
            self._create_dict(
                self._table_cols_lookup("media"),
                item,
            ) for item in items
        ]

    def get_all(self, table):
        self._execute(f"SELECT * FROM {table};")
        items = self._fetchall()
        if items is None:
            raise NotFound(f"no items in {table}")

        return [
            self._create_dict(
                self._table_cols_lookup(table),
                item,
            ) for item in items
        ]

    @staticmethod
    def upload_media(**kwargs):
        with connection() as postgres:
            postgres.insert(
                "mediaV2",
                list(kwargs.keys()),
                [list(kwargs.values())],
            )

    @staticmethod
    def media_has_been_sent(id):
        with connection() as postgres:
            postgres.update_field("mediaV2", "has_been_sent", True, id)

    @staticmethod
    def get_by_id(id):
        item = None
        with connection() as postgres:
            item = postgres.get_by_id("mediaV2", id)

        return item

    @staticmethod
    def get_random_by_category(category, filter_key=None, filter_val=None):
        item = None
        with connection() as postgres:
            items = postgres.get_all_by_category(category)
            if filter_key:
                items = Postgres.filter_db_row(items, filter_key, filter_val)

            try:
                item = choice(items)
            except IndexError:
                pass

        return item

    @staticmethod
    def filter_db_row(row, key, val=None):
        filtered_items = []
        for item in row:
            needle = item.get(key, False)
            if needle and needle == val:
                filtered_items.append(item)
            elif needle and not val:
                filtered_items.append(item)

        return filtered_items


@contextlib.contextmanager
def connection():
    postgres = None
    try:
        postgres = Postgres()
        postgres.connect()
        yield postgres
    except Exception as e:
        print(e)
    finally:
        if postgres:
            postgres.disconnect()
