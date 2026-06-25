import sqlite3
from contextlib import contextmanager


class Search:
    database = 'searches.db'

    with sqlite3.connect(database) as __conn:
        __conn.execute("CREATE TABLE IF NOT EXISTS searches ("
                       "id    INTEGER PRIMARY KEY,"
                       "title TEXT    NOT NULL)")
        __conn.execute("CREATE TABLE IF NOT EXISTS search_terms("
                       "search_id INTEGER REFERENCES searches(id) ON DELETE CASCADE,"
                       "term      TEXT    NOT NULL)")
        __conn.commit()
    __conn.close()

    @staticmethod
    @contextmanager
    def get_conn(db=database):
        conn = sqlite3.connect(db)
        try:
            yield conn
        finally:
            conn.close()

    # CREATE
    @classmethod
    def create_search(cls, title: str, terms: list[str]):
        with cls.get_conn() as conn:
            cur = conn.execute("INSERT INTO searches(title) VALUES (?)", (title,))
            search_id = cur.lastrowid
            for term in terms:
                conn.execute("INSERT INTO search_terms(search_id, term) VALUES (?, ?)", (search_id, term))

    # READ
    @classmethod
    def get_all_searches(cls) -> list[tuple[str, str]]:
        with cls.get_conn() as conn:
            cur = conn.execute("SELECT * FROM searches")
            return cur.fetchall()

    # READ
    @classmethod
    def get_search(cls, search_id: int) -> tuple[str, str] | None:
        with cls.get_conn() as conn:
            cur = conn.execute("SELECT * FROM searches WHERE id = (?)", (search_id,))
            return cur.fetchone()

    # DELETE
    @classmethod
    def delete_search(cls, search_id: int) -> bool | None:
        with cls.get_conn() as conn:
            cur = conn.execute("DELETE FROM searches WHERE id = (?)", (search_id,))
            if cur.rowcount == 1:
                return True
            else:
                return None
