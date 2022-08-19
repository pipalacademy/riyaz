from collections import namedtuple

from . import db
from . import models


ModuleLessonIndex = namedtuple(
    "ModuleLessonIndex", ["module_index", "lesson_index"]
)


class Course(db.Document):
    DOCTYPE = "course"

    def get_lesson(self, module_name, lesson_name):
        return Lesson.find(
            course=self.key, module=module_name, name=lesson_name
        )

    def get_module_index(self, module_name):
        module_i = next(
            (
                idx
                for idx, module in enumerate(self.outline, 1)
                if module["name"] == module_name
            ),
            None,
        )

        return module_i

    def get_lesson_index(self, module_name, lesson_name):
        module_i = self.get_module_index(module_name)
        if not module_i:
            return

        module = self.outline[module_i - 1]
        lesson_i = next(
            (
                idx
                for idx, lesson in enumerate(module["lessons"], 1)
                if lesson["name"] == lesson_name
            ),
            None,
        )

        return lesson_i and ModuleLessonIndex(module_i, lesson_i)

    def get_next_lesson(self, lesson):
        flattened_lessons = [
            {"module_name": _module["name"], "lesson_name": _lesson["name"]}
            for _module in self.outline
            for _lesson in _module["lessons"]
        ]
        idx = flattened_lessons.index(
            {"module_name": lesson.module, "lesson_name": lesson.name}
        )

        if idx + 1 < len(flattened_lessons):
            return self.get_lesson(**flattened_lessons[idx + 1])

        return

    def get_previous_lesson(self, lesson):
        flattened_lessons = [
            {"module_name": _module["name"], "lesson_name": _lesson["name"]}
            for _module in self.outline
            for _lesson in _module["lessons"]
        ]
        idx = flattened_lessons.index(
            {"module_name": lesson.module, "lesson_name": lesson.name}
        )

        if idx - 1 >= 0:
            return self.get_lesson(**flattened_lessons[idx - 1])

        return

    @property
    def lessons(self):
        return Lesson.find_all(course=self.key)

    @property
    def modules(self):
        return Module.find_all(course=self.key)

    @classmethod
    def save_from_model(cls, _course: models.Course):
        course_data = _course.dict()
        modules = course_data.pop("outline")
        course_data["outline"] = create_outline_without_content(modules)
        course = cls(_course.name, course_data)
        course.save()

        # save modules and lessons
        for module_data in modules:
            lessons = module_data.pop("lessons")
            module = Module(
                module_data["name"], {**module_data, "course": course.key}
            ).save()

            for lesson_data in lessons:
                Lesson(
                    f"{module.key}/{lesson_data['name']}",
                    {
                        **lesson_data,
                        "module": module.key,
                        "course": course.key,
                    },
                ).save()

        return course


class Module(db.Document):
    DOCTYPE = "module"

    def get_course(self):
        return Course.find(key=self.course)

    @property
    def lessons(self):
        return Lesson.find_all(course=self.course, module=self.key)

    @property
    def index(self):
        course = self.get_course(course=self.key)
        return course and course.get_module_index(self.name)


class Lesson(db.Document):
    DOCTYPE = "lesson"

    def get_module(self):
        return Module.find(course=self.course, name=self.module)

    def get_course(self):
        return Course.find(key=self.course)

    @property
    def index(self):
        course = self.get_course()
        return course and course.get_lesson_index(self.module, self.name)

    @property
    def next(self):
        course = self.get_course()
        return course and course.get_next_lesson(self)

    @property
    def previous(self):
        course = self.get_course()
        return course and course.get_previous_lesson(self)

    def get_url(self):
        return f"/courses/{self.course}/{self.module}/{self.name}"


def create_outline_without_content(modules):
    # strip lesson content from outline
    return [
        {
            "name": module["name"],
            "title": module["title"],
            "lessons": [
                {"name": lesson["name"], "title": lesson["title"]}
                for lesson in module["lessons"]
            ],
        }
        for module in modules
    ]


db.register_model(Course)
db.register_model(Module)
db.register_model(Lesson)
