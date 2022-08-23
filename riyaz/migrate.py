from .db import get_db
from pathlib import Path

def migrate():
    """Migrate the database to the latest version.
    """
    init_schema()

def get_tables():
    q = "select name from sqlite_master where type='table'"
    rows = get_db().query(q)
    return [row.name for row in rows]

def has_table(name):
    return name in get_tables()

def init_schema():
    if not has_table("course"):
        schema = Path(__file__).parent.joinpath("schema.sql").read_text()
        cursor = get_db().ctx.db.cursor()
        cursor.executescript(schema)

if __name__ == "__main__":
    migrate()