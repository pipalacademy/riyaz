
from . import db

class Course(db.Document):
    pass

db.register_model("course", Course)
