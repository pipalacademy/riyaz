from pathlib import Path
from .disk import CourseLoader

query_fields = {
    "module": ("course", "name"),
    "lesson": ("course", "module", "name")
}

def load_sample_data(path: str):
    """Loads sample data from given path.
    """
    paths = Path(path).glob("*/")
    for p in paths:
        print(f"loading {p} ...")
        CourseLoader(p).load()

# def load_course(doc):
#     keys = ['key', 'title', 'short_description', 'description']
#     doc = {k: doc[k] for k in keys}
#     course = Course.find(key=doc['key'])
#     if course:
#         course.update(**doc)
#     else:
#         course = Course(**doc)
#     print(course)
#     course.save()
#     return course
