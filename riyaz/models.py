
from . import db

class Course(db.Document):
    DOCTYPE = "course"

    def get_lesson(self, module_name, lesson_name):
        return Lesson.find(course=self.key, module=module_name, name=lesson_name)

class Module(db.Document):
    DOCTYPE = "module"
    pass

class Lesson(db.Document):
    DOCTYPE = "lesson"

    def get_module(self):
        return Module.find(course=self.course, name=self.module)

    @property
    def next(self):
        collection = db.query("lesson", index=self.index+1)
        return collection and collection[0] or None

    @property
    def previous(self):
        collection = db.query("lesson", index=self.index-1)
        return collection and collection[0] or None

    def get_url(self):
        return f"/courses/{self.course}/{self.module}/{self.name}"

db.register_model(Course)
db.register_model(Module)
db.register_model(Lesson)
