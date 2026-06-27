import sqlite3
from contextlib import closing


class SearchTerm:
    def __init__(self, id_: int, term: str):
        self.id = id_
        self.term = term

    def __repr__(self):
        return f"ST[id={self.id}, term=\"{self.term}\"]"


class Search:
    database = 'searches.db'

    def __init__(self, id_: int, title: str, search_terms: list[SearchTerm]):
        self.id = id_
        self.title = title
        self.search_terms = search_terms

    def __repr__(self):
        return f"Search[id={self.id}, title=\"{self.title}\", search_terms={self.search_terms}]"

    @classmethod
    def init_db(cls):
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                conn.execute("CREATE TABLE IF NOT EXISTS searches ("
                             "id    INTEGER PRIMARY KEY,"
                             "title TEXT    NOT NULL)")
                conn.execute("CREATE TABLE IF NOT EXISTS search_terms("
                             "id        INTEGER PRIMARY KEY,"
                             "search_id INTEGER REFERENCES searches(id) ON DELETE CASCADE,"
                             "term      TEXT    NOT NULL)")
                conn.commit()

    # ========================================
    # CREATE
    # ========================================

    @classmethod
    def create_search(cls, title: str, terms: list[str]) -> int | None:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                cursor = conn.execute("INSERT INTO searches(title) VALUES (?)", (title,))
                search_id = cursor.lastrowid
                # guard necessary here because we otherwise might try to insert None
                if search_id is None:
                    return None

                for term in terms:
                    conn.execute("INSERT INTO search_terms(search_id, term) VALUES (?, ?)", (search_id, term))

                return search_id

    @classmethod
    def create_search_term(cls, search_id: int, term: str) -> int | None:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                cursor = conn.execute("INSERT INTO search_terms(search_id, term) VALUES (?, ?)", (search_id, term))
                return cursor.lastrowid

    # ========================================
    # READ
    # ========================================

    @classmethod
    def get_all_searches(cls) -> list["Search"]:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                # TODO: naive implementation
                cursor = conn.execute("SELECT * FROM searches")
                ret_searches: dict[int, Search] = {}
                for x in cursor.fetchall():
                    ret_searches[x[0]] = Search(id_=x[0], title=x[1], search_terms=[])
                for key in ret_searches:
                    cursor = conn.execute("SELECT id, term FROM search_terms WHERE search_id = (?)",
                                          (ret_searches[key].id,))
                    for x in cursor.fetchall():
                        ret_searches[key].search_terms.append(SearchTerm(id_=x[0], term=x[1]))

                return list(ret_searches.values())

    @classmethod
    def get_search(cls, search_id: int) -> "Search | None":
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                cursor = conn.execute("SELECT * FROM searches WHERE id = (?)", (search_id,))
                x = cursor.fetchone()
                if x is None:
                    return None
                else:
                    ret_search = Search(id_=x[0], title=x[1], search_terms=[])
                    cursor = conn.execute("SELECT id, term FROM search_terms WHERE search_id = (?)",
                                          (ret_search.id,))
                    for x in cursor.fetchall():
                        ret_search.search_terms.append(SearchTerm(id_=x[0], term=x[1]))

                    return ret_search

    # ========================================
    # UPDATE
    # ========================================

    @classmethod
    def update_search_title(cls, search_id: int, new_title: str) -> None:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                conn.execute("UPDATE searches SET title = (?) WHERE id = (?)", (new_title, search_id))

    @classmethod
    def update_search_term(cls, search_id: int, term_id: int, new_term: str) -> None:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                conn.execute("UPDATE search_terms SET term = (?) WHERE id = (?) and search_id = (?)",
                             (new_term, term_id, search_id))

    # ========================================
    # DELETE
    # ========================================

    @classmethod
    def delete_search(cls, search_id: int) -> bool | None:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                cursor = conn.execute("DELETE FROM searches WHERE id = (?)", (search_id,))
                if cursor.rowcount == 1:
                    return True
                else:
                    return None

    @classmethod
    def delete_search_term(cls, search_id: int, term_id: int) -> bool | None:
        with closing(sqlite3.connect(cls.database)) as conn:
            with conn:
                cursor = conn.execute("DELETE FROM search_terms WHERE id = (?) and search_id = (?)",
                                      (term_id, search_id))
                if cursor.rowcount == 1:
                    return True
                else:
                    return None
