import sqlite3
from contextlib import closing


class SearchTerm:
    def __init__(self, id_: int, term: str):
        self.id = id_
        self.term = term


class Search:
    database = 'searches.db'

    def __init__(self, id_: int, title: str, search_terms: list[SearchTerm]):
        self.id = id_
        self.title = title
        self.search_terms = search_terms

    @classmethod
    def init_db(cls):
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                conn.execute("CREATE TABLE IF NOT EXISTS searches ("
                             "id    INTEGER PRIMARY KEY,"
                             "title TEXT    NOT NULL)")
                conn.execute("CREATE TABLE IF NOT EXISTS search_terms("
                             "search_id INTEGER REFERENCES searches(id) ON DELETE CASCADE,"
                             "term      TEXT    NOT NULL)")
                conn.commit()

    # CREATE
    @classmethod
    def create_search(cls, title: str, terms: list[str]):
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                print("adding:", title, "with", terms)
                cursor = conn.execute("INSERT INTO searches(title) VALUES (?)", (title,))
                search_id = cursor.lastrowid
                for term in terms:
                    conn.execute("INSERT INTO search_terms(search_id, term) VALUES (?, ?)", (search_id, term))

    # READ
    @classmethod
    def get_all_searches(cls) -> list[tuple[str, str]]:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                cursor = conn.execute("SELECT * FROM searches")
                return cursor.fetchall()

    # READ
    @classmethod
    def get_search(cls, search_id: int) -> tuple[str, str] | None:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                cursor = conn.execute("SELECT * FROM searches WHERE id = (?)", (search_id,))
                return cursor.fetchone()

    # DELETE
    @classmethod
    def delete_search(cls, search_id: int) -> bool | None:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                cursor = conn.execute("DELETE FROM searches WHERE id = (?)", (search_id,))
                if cursor.rowcount == 1:
                    return True
                else:
                    return None
