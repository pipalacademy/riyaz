"""database of riyaz.
"""
from __future__ import annotations
import web
import functools
from itertools import groupby
from pydantic import BaseModel
from typing import List, Optional
from . import config

class SqliteDB(web.db.SqliteDB):
    def _connect(self, keywords):
        conn = super()._connect(keywords)
        conn.execute("PRAGMA foreign_keys = 1")
        return conn

    def _connect_with_pooling(self, keywords):
        conn = super()._connect_with_pooling(keywords)
        conn.execute("PRAGMA foreign_keys = 1")
        return conn

web.db.register_database("sqlite", SqliteDB)

@web.memoize
def get_db():
    return web.database("sqlite:///" + config.database_path)

cache = {}

def query_memoize(f):
    @functools.wraps(f)
    def g(cls, **kwargs):
        key = cls, tuple(kwargs.items())
        if key not in cache:
            cache[key] = f(cls, **kwargs)
        return cache[key]
    return g

class Document(BaseModel):
    id: Optional[int] = None

    @classmethod
    def find(cls, **kwargs):
        docs = cls.find_all(**kwargs, limit=1)
        return docs and docs[0] or None

    @classmethod
    @query_memoize
    def find_all(cls, **kwargs):
        rows = get_db().where(cls._TABLE, **kwargs)
        return [cls(**row) for row in rows]

    @classmethod
    def select(cls, *, what='*', where, vars, order=None, limit=None, offset=None):
        rows = get_db().select(
            cls._TABLE,
            what=what,
            where=where,
            vars=vars,
            order=order,
            limit=limit,
            offset=offset)
        if what == '*':
            return [cls(**row) for row in rows]
        else:
            return rows

    def __repr__(self):
        return f"<{self.__class__.__name__} {dict(self)}>"

    __str__ = __repr__

    def update(self, **kwargs):
        # TODO: is there a better way to handle this?
        self.__dict__.update(kwargs)

    def save(self):
        if self.id is None:
            d = self.dict()
            d.pop("id", None)
            self.id = get_db().insert(self._TABLE, **d)
        else:
            get_db().update(self._TABLE, where="id=$id", vars={"id": self.id}, **self.dict())

class Course(Document):
    _TABLE = "course"

    key: str
    title: str
    short_description: Optional[str]
    description: Optional[str]

    def get_modules(self):
        return Module.find_all(course_id=self.id)

    def get_module(self, name):
        return Module.find(course_id=self.id, name=name)

    def get_lesson(self, name):
        return Lesson.find(course_id=self.id, name=name)

    def get_outline(self):
        outline_lessons = get_db().select(
            "course_outline",
            where="course_id = $course_id",
            order="module_index, lesson_index",
            vars={"course_id": self.id})

        def transform(lesson_group):
            first = lesson_group[0]
            module = Module.find(id=first["module_id"])
            return {
                "name": module.name,
                "title": module.title,
                "index": first["module_index"],
                "lessons": [
                    {
                        **Lesson.find(id=outline["lesson_id"]).get_preview(),
                        "index": outline["lesson_index"],
                    }
                    for outline in lesson_group
                ]
            }

        return [transform(list(lesson_group))
                for _, lesson_group in groupby(
                    outline_lessons, lambda x: x.module_id)]

    def get_instructors(self):
        return Instructor.find_by_course(self)

    def set_instructors(self, *instructors):
        get_db().delete(
            "course_instructor",
            where="course_id = $course_id", vars={"course_id": self.id})

        for idx, instructor in enumerate(instructors):
            if instructor.id is None:
                instructor.save()

            get_db().insert(
                "course_instructor",
                course_id=self.id, instructor_id=instructor.id, index_=idx)

    def set_outline(self, outline: List[CourseOutline]):
        assert self.id is not None  # should not be unsaved

        get_db().delete(
                "course_outline",
                where="course_id = $course_id", vars={"course_id": self.id})

        for lesson_outline in outline:
            assert lesson_outline.course_id == self.id
            lesson_outline.save()

        return outline


class Instructor(Document):
    _TABLE = "instructor"

    key: str
    name: str
    about: str
    photo_path: Optional[str]

    def get_preview(self):
        return {"id": self.id, "key": self.key, "name": self.name}

    def get_courses(self):
        rows = get_db().where("course_instructor", instructor_id=self.id)
        course_ids = [row.course_id for row in rows]
        # return Course.select(where="id in $ids", vars={"ids": course_ids})

        return Course.select(
            join={"course_instructor": "course_instructor.course_id=course.id"},
            where="course_instructor.instructor_id=$id", vars={"id": self.id})

    @classmethod
    def find_by_course(cls, course):
        rows = get_db().where("course_instructor", course_id=course.id)
        ids = [row.instructor_id for row in rows]
        return cls.select(where="id in $ids", vars={"ids": ids})


class Module(Document):
    _TABLE = "module"

    course_id: int
    name: str
    title: str
    index_: int

    def get_lessons(self):
        return Lesson.find_all(module_id=self.id)

class Lesson(Document):
    _TABLE = "lesson"

    course_id: int
    module_id: int
    index_: int
    name: str
    title: str
    content: Optional[str]

    def get_course(self):
        return Course.find(id=self.course_id)

    def get_preview(self):
        return dict(id=self.id, name=self.name, title=self.title)

    def get_next(self):
        row = get_db().select("course_outline", lesson_id=self.id).first()
        return row and row.next_lesson_id and Lesson.find(id=row.next_lesson_id) or None

    def get_prev(self):
        row = get_db().select("course_outline", lesson_id=self.id).first()
        return row and row.next_lesson_id and Lesson.find(id=row.next_lesson_id) or None


class CourseOutline(Document):
    _TABLE = "course_outline"

    course_id: int

    module_id: int
    module_index: int

    lesson_id: int
    lesson_index: int

    prev_lesson_id: Optional[int]
    prev_lesson_index: Optional[int]

    next_lesson_id: Optional[int]
    next_lesson_index: Optional[int]

    orphan: Optional[bool]
