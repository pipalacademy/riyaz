from pathlib import Path
import yaml
from . import db

def load_sample_data(path: str):
    """Loads sample data from given path.
    """
    paths = Path(path).glob("*.yml")
    for p in paths:
        print(f"loading {p} ...")
        doc = yaml.safe_load(p.open())
        doctype = doc.pop('doctype')
        key = doc.pop('key')
        db.save(doctype, key, doc)