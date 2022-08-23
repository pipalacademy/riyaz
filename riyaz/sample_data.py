from pathlib import Path
import yaml
import uuid
from .db import Course, Lesson, Module

query_fields = {
    "module": ("course", "name"),
    "lesson": ("course", "module", "name")
}

def load_sample_data(path: str):
    """Loads sample data from given path.
    """
    paths = Path(path).glob("*.yml")
    for p in paths:
        print(f"loading {p} ...")
        doc = yaml.safe_load(p.open())
        doctype = doc.pop('doctype')
        # db.save(doctype, key, doc)
        if doctype == 'course':
            load_course(doc)

def load_course(doc):
    keys = ['key', 'title', 'short_description', 'description']
    doc = {k: doc[k] for k in keys}
    course = Course.find(key=doc['key'])
    if course:
        course.update(**doc)
    else:
        course = Course(**doc)
    print(course)
    course.save()
    return course
