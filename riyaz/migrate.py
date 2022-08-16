from . import db
from pathlib import Path

def migrate():
    """Migrate the database to the latest version.
    """
    init_schema()

def get_tables():
    q = "select name from sqlite_schema where type='table'"
    with db.get_connection() as con:
        cur = con.cursor()
        cur.execute(q)
        rows = cur.fetchall()
        return [row[0] for row in rows]

def has_table(name):
    return name in get_tables()

def init_schema():
    if not has_table("document"):
        schema = Path(__file__).parent.joinpath("schema.sql").read_text()
        with db.get_connection() as con:
            cur = con.cursor()
            cur.execute(schema)