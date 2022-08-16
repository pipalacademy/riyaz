"""Document database for riyaz.

It is a simple schemaless document database built on sqlite.

Requires Sqlite version 3.8.0+.

## Usage

    from riyaz import db

    db.save("number", "one", {"name": "One", "value": 1, "parity", "odd"})
    db.save("number", "two", {"name": "Two", "value": 2, "parity": "even"})
    db.save("number", "three", {"name": "Three", "value": 3, "parity": "odd"})

    doc = db.get("number", "one")
    print(doc.name, doc.value) # one 1

    db.query(doctype="number", value=2) # [<number:two>]

    db.query(doctype="number", parity='odd') # [<number:one>, <number:three>]

    db.get_many("number": ["one", "two"]) # [<number:one>, <number:two>]

## Inspiration

This is inspired by Infogami[1][2] and FriendFeed database[3].

[1]: https://github.com/openlibrary/infogami/blob/a4677e19ec0c6f7bafeb0bbdf166ff078b71d3dc/infogami/tdb/schema.sql
[2]: https://github.com/openlibrary/infogami
[3]: https://backchannel.org/blog/friendfeed-schemaless-mysql
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re
import apsw
import json

from . import config

def verify_sqlite_version():
    version = apsw.sqlitelibversion()
    print("Sqlite version:", version)
    v = version.split(".")
    if v < ['3', '38']:
        raise Exception("This software requires use sqlite >= 3.38.0")
    print(apsw.SQLITE_VERSION_NUMBER)

verify_sqlite_version()

def get_connection():
    return apsw.Connection(config.database_path)

class Document:
    def __init__(self, doctype, key, data, id=None):
        self.__dict__['id'] = id
        self.__dict__['doctype'] = doctype
        self.__dict__['key'] = key
        self.__dict__['data'] = data

    def __repr__(self):
        return f"<{self.doctype} {self.key} {self.data}>"

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data['key'] = value

    def __getattr__(self, key):
        if key.startswith("_"):
            return super().__getattr__(key)

        try:
            return self.data[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            return super().__setattr__(key, value)

        self.data[key] = value

RE_FIELD = re.compile(r"^\w+$")

@dataclass
class DBQuery:
    """Structure for database query"""
    table: str = "document"
    where_clauses: List[str] = field(default_factory=list)
    params: List[Any] = field(default_factory=list)

    def clone(self):
        return DBQuery(self.table, list(self.where_clauses), list(self.params))

    def where(self, name, value, op="="):
        if not RE_FIELD.match(name):
            raise ValueError(f"Invalid field: {name}")

        if name in ['key', 'doctype']:
            field = name
        else:
            field = f"data->>'$.{name}'"

        clause, params = self._prepare_where(field, op, value)

        q = self.clone()
        q.where_clauses.append(clause)
        q.params.extend(params)
        return q

    def _prepare_where(self, field, op, value):
        """Returns the clause and params."""
        if isinstance(value, list):
            n = len(value)
            placeholder = "(" + ", ".join('?' * n) + ")"
            params = value
        else:
            placeholder = "?"
            params = [value]
        return f"{field} {op} {placeholder}", params

    def make_query(self):
        sql = "SELECT id, doctype, key, data FROM document"
        if self.where_clauses:
            sql += " WHERE " + " AND ".join(self.where_clauses)
        return sql

    def execute(self, con):
        sql = self.make_query()
        print("execute:", sql)
        cur = con.cursor()
        cur.execute(sql, self.params)
        rows = cur.fetchall()
        return [self.process_row(row) for row in rows]

    def process_row(self, row):
        _id, doctype, key, data = row
        data = json.loads(data)
        return Document(doctype, key, data, id=_id)

def get(doctype: str, key: str) -> Optional[Document]:
    """Returns a document from database.
    """
    q = (
        DBQuery()
        .where("doctype", doctype)
        .where("key", key))
    with get_connection() as con:
        docs = q.execute(con)
        return docs and docs[0] or None

def get_many(doctype: str, keys: List[str]) -> List[Document]:
    """Loads and returns multiple documents at once from the database.
    """
    q = (
        DBQuery()
        .where("doctype", doctype)
        .where("key", keys, op="IN"))
    with get_connection() as con:
        docs = {doc.key: doc for doc in q.execute(con)}
        return [docs[key] for key in keys]

def query(doctype: str, **where: Dict[str, Any]) -> List[Document]:
    """Queries the database and returns the matching documents.
    """
    q = DBQuery()
    q = q.where('doctype', doctype)
    for name, value in where.items():
        q = q.where(name, value)

    with get_connection() as con:
        return q.execute(con)

def save(doctype: str, key: str, data: Dict[str, Any]) -> Document:
    """Saves a new document or updates an existing one in the database.
    """
    doc = get(doctype, key)
    if doc:
        q = "UPDATE document SET data=? WHERE id=?"
        params = [json.dumps(data), doc.id]
    else:
        q = "INSERT INTO document (doctype, key, data) VALUES (?, ?, ?)"
        params = [doctype, key, json.dumps(data)]

    with get_connection() as con:
        cur = con.cursor()
        print("execute:", q)
        cur.execute(q, params)

    doc = get(doctype, key)
    if doc is None:
        raise Exception("bah")
    return doc
