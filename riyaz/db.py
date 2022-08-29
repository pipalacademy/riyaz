"""database of riyaz.
"""
from __future__ import annotations
import web
import functools
import random
import shutil
import string
from datetime import datetime
from itertools import groupby
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional, Union
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

    def get_lesson(self, module_name, lesson_name):
        module = self.get_module(module_name)
        return Lesson.find(
            course_id=self.id, module_id=module.id, name=lesson_name)

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

    def update_version(self):
        hash_value = get_random_string(16)
        Store.set(self.key, hash_value)
        return hash_value

    def new_asset(self, filename: str) -> Asset:
        assert self.id is not None

        return Asset(
            collection="courses", collection_id=self.id, filename=filename)


class Instructor(Document):
    _TABLE = "instructor"

    key: str
    name: str
    about: str
    photo_id: Optional[int]

    def get_preview(self):
        return {"id": self.id, "key": self.key, "name": self.name}

    def get_courses(self):
        rows = get_db().where("course_instructor", instructor_id=self.id)
        course_ids = [row.course_id for row in rows]
        # return Course.select(where="id in $ids", vars={"ids": course_ids})

        return Course.select(
            join={"course_instructor": "course_instructor.course_id=course.id"},
            where="course_instructor.instructor_id=$id", vars={"id": self.id})

    def new_asset(self, filename: str) -> Asset:
        assert self.id is not None

        return Asset(
            collection="instructors", collection_id=self.id, filename=filename)

    def get_asset(self, filename: str) -> Optional[Asset]:
        return Asset.find(
            collection="instructors", collection_id=self.id, filename=filename)

    def get_photo_url(self) -> Optional[str]:
        asset = self.photo_id and Asset.find(id=self.photo_id)
        return asset and asset.get_url() or None

    def set_photo(self, asset: Union[Asset, None]):
        self.photo_id = asset and asset.id or None
        return self.photo_id

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

    @classmethod
    def new(cls, course: Course, name: str, title: str, index_: int = 1):
        return cls(...)

    def get_lessons(self):
        return Lesson.find_all(module_id=self.id)

    def get_lesson(self, name):
        return Lesson.find(module_id=self.id, name=name)

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

    def get_module(self):
        return Module.find(id=self.module_id)

    def get_preview(self):
        return dict(id=self.id, name=self.name, title=self.title)

    def get_url(self):
        course = self.get_course()
        module = self.get_module()
        return f"/courses/{course.key}/{module.name}/{self.name}"

    def get_label(self):
        """Return a label `{module_index}.{lesson_index}`, like 1.1, 2.4
        """
        row = CourseOutline.find(lesson_id=self.id)
        return row and f"{row.module_index}.{row.lesson_index}"

    def get_next(self):
        row = CourseOutline.find(lesson_id=self.id)
        return row and row.next_lesson_id and Lesson.find(id=row.next_lesson_id) or None

    def get_prev(self):
        row = CourseOutline.find(lesson_id=self.id)
        return row and row.prev_lesson_id and Lesson.find(id=row.prev_lesson_id) or None


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


class Store(Document):
    _TABLE = "store"

    key: str
    value: str

    @classmethod
    def get(cls, key):
        row = cls.find(key=str(key))
        return row and row.value or None

    @classmethod
    def set(cls, key, value):
        if kv := cls.find(key=key):
            kv.value = value
        else:
            kv = cls(key=key, value=value)

        return kv.save()


class Asset(Document):
    _TABLE = "asset"

    collection: str
    collection_id: int
    filename: str

    filesize: Optional[int]
    created: Optional[datetime]
    last_modified: Optional[datetime]

    def _get_full_identifier(self):
        return f"{self.collection}/{self.collection_id}/{self.filename}"

    def _construct_asset_path(self):
        if "/" in self.filename:
            assert ValueError(f"Filename '{self.filename}' cannot be a path")

        full_identifier = self._get_full_identifier()
        return Path(config.assets_path) / full_identifier

    def get_url(self):
        assets_root = "/assets/"

        full_identifier = self._get_full_identifier()
        return f"{assets_root}{full_identifier}"

    def save_file(self, on_disk_path: Path):
        if not on_disk_path.is_file():
            raise ValueError(f"Path {str(on_disk_path)} is not a file")

        asset_path = self._construct_asset_path()

        filesize = on_disk_path.stat().st_size
        self.filesize = filesize

        asset_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(on_disk_path, asset_path)

        self.update_timestamps()
        self.save()

        return asset_path

    def update_timestamps(self):
        now = datetime.now()

        if self.id is None or self.created is None:
            self.created = now

        self.last_modified = now


def get_random_string(length):
    return "".join([ch for _ in range(length)
                    for ch in random.choice(string.ascii_letters)])
