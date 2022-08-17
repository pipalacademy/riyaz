
from . import db

class Course(db.Document):
    @classmethod
    def find(cls, key):
        return db.get("course", key)

    @classmethod
    def all(cls):
        return db.query("course")

    def get_lesson(self, module_name, lesson_name):
        # TODO: Use self.id or self.key to query from only
        # those lessons that belong to this course
        lesson_key = f"{module_name}/{lesson_name}"
        return db.get("lesson", lesson_key)

class Module(db.Document):
    pass

class Lesson(db.Document):
    @property
    def module(self):
        parts = self.key.split("/", 1)
        if len(parts) == 2:
            module_key = parts[0]
            return db.get("module", module_key)
        else:
            return None

    @property
    def next(self):
        collection = db.query("lesson", index=self.index+1)
        return collection and collection[0] or None

    @property
    def previous(self):
        collection = db.query("lesson", index=self.index-1)
        return collection and collection[0] or None

db.register_model("course", Course)
db.register_model("module", Module)
db.register_model("lesson", Lesson)
