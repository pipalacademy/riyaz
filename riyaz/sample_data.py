from pathlib import Path
import yaml
import uuid
from . import db

query_fields = {
    "module": ("course", "name"),
    "lesson": ("course", "module", "name")
}

def find_key(doc):
    """Find the key of the document in the db.

    If the a matching document is not found in db then it returns a new UUID as key.
    """
    doctype = doc['doctype']
    if doctype not in query_fields:
        raise ValueError("Generating key is not supported for doctype:", doctype)
    fields = query_fields[doctype]
    q = {field: doc[field] for field in fields}
    db_doc = db.find(doctype, **q)
    return db_doc and db_doc.key or uuid.uuid4().hex

def load_sample_data(path: str):
    """Loads sample data from given path.
    """
    paths = Path(path).glob("*.yml")
    for p in paths:
        print(f"loading {p} ...")
        doc = yaml.safe_load(p.open())
        key = doc.pop('key', None) or find_key(doc)
        doctype = doc.pop('doctype')
        db.save(doctype, key, doc)