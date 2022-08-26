"""
pydantic models and utility functions for parsing the on-disk courses go here.
"""
from __future__ import annotations

import re
from itertools import tee
from pathlib import Path
from typing import Any, Iterator, List, Optional, Tuple, Union

import frontmatter
import yaml
from pydantic import BaseModel, HttpUrl, validate_arguments, validator
from pydantic.types import DirectoryPath, FilePath

from . import models
from . import db


class DiskChapter(BaseModel):
    base_dir: DirectoryPath = Path(".")
    name: str
    title: str
    lessons: List[FilePath]

    @validator("lessons", each_item=True, pre=True)
    def prepend_base_dir_to_lessons(cls, v, values):
        if isinstance(v, str) or isinstance(v, Path):
            return values["base_dir"] / v

        return v

    def parse(self) -> models.Chapter:
        lessons = [get_lesson_from_path(path) for path in self.lessons]
        return models.Chapter(
            name=self.name, title=self.title, lessons=lessons
        )


class DiskCourse(BaseModel):
    base_dir: DirectoryPath = Path(".")
    name: str
    title: str
    short_description: Optional[str]
    description: str
    authors: List[str]
    outline: List[DiskChapter]

    @validator("authors", each_item=True)
    def check_author_file_exists(cls, v, values):
        author_file = get_author_file_path(values["base_dir"], v)
        if not author_file.exists():
            raise ValueError(f"author file {author_file} does not exist")

        return v

    @validator("outline", each_item=True, pre=True)
    def add_base_dir_to_outline(cls, v, values):
        if isinstance(v, dict):
            v["base_dir"] = v.get("base_dir", values["base_dir"])

        return v

    def get_author_from_key(self, key):
        path = get_author_file_path(self.base_dir, key)
        fm = frontmatter.load(path)

        return models.Author(
            key=key,
            name=fm.get("name"),
            photo=fm.get("photo"),
            about=fm.content,
        )

    def parse(self) -> models.Course:
        authors = [self.get_author_from_key(key) for key in self.authors]
        outline = [disk_chapter.parse() for disk_chapter in self.outline]
        return models.Course(
            name=self.name,
            title=self.title,
            short_description=self.short_description,
            description=self.description,
            authors=authors,
            outline=outline,
        )


@validate_arguments
def get_course_from_directory(directory: DirectoryPath) -> models.Course:
    disk_course = read_config(directory / "course.yml")
    return disk_course.parse()


@validate_arguments
def read_config(path: FilePath) -> DiskCourse:
    with open(path) as f:
        config_dict = yaml.safe_load(f)

    config_dict["base_dir"] = config_dict.get("base_dir", path.parent)
    course = DiskCourse.parse_obj(config_dict)

    return course


@validate_arguments
def get_lesson_from_path(path: FilePath) -> models.Lesson:
    name = path.name.split(".", 1)[0]
    with open(path) as f:
        content = f.read()
        title = get_first_heading(content) or titlify(name)

    return models.Lesson(name=name, title=title, content=content)


def get_author_file_path(base_dir: DirectoryPath, key: str):
    return base_dir / "authors" / f"{key}.md"


def get_first_heading(content: str) -> Optional[str]:
    heading_regex = re.compile(r"^(?:#{1,6})(.+)", re.MULTILINE)

    if m := heading_regex.search(content):
        return m.group(1).strip()

    return None


def titlify(s: str) -> str:
    to_replace = r"[-_(\s+)]"
    unsymbol = re.sub(to_replace, " ", s)

    return unsymbol.title()


class CourseLoader:
    def __init__(self, path: DirectoryPath):
        self.path = path

    def load(self):
        parsed_course = get_course_from_directory(self.path)
        course = self._load_course(parsed_course)
        course.save()

        instructors = [
            self._load_author(author)
            for idx, author in enumerate(parsed_course.authors)
        ]
        course.set_instructors(*instructors)

        course_outline = []
        for m_idx, chapter in enumerate(parsed_course.outline, start=1):
            module = self._load_chapter(
                course_id=course.id, index=m_idx, chapter=chapter
            )
            module.save()

            for l_idx, parsed_lesson in enumerate(chapter.lessons, start=1):
                lesson = self._load_lesson(
                    course_id=course.id,
                    module_id=module.id,
                    index=l_idx,
                    lesson=parsed_lesson,
                )
                lesson.save()

                lesson_outline = self._load_lesson_outline(
                    course.id,
                    module.id,
                    lesson.id,
                    module_index=m_idx,
                    lesson_index=l_idx,
                )
                course_outline.append(lesson_outline)

        course_outline = self._load_outline(course_outline)
        course.set_outline(course_outline)
        course.update_version()

        return course

    def _load_course(self, course: models.Course) -> db.Course:
        fields = dict(
            key=course.name,
            title=course.title,
            short_description=course.short_description,
            description=course.description
        )

        if db_course := db.Course.find(key=course.name):
            db_course.update(**fields)
        else:
            db_course = db.Course(**fields)

        return db_course

    def _load_chapter(
        self, course_id: int, index: int, chapter: models.Chapter
    ) -> db.Module:
        course = db.Course.find(id=course_id)
        assert course is not None

        fields = dict(
            course_id=course_id,
            name=chapter.name,
            title=chapter.title,
            index_=index,
        )

        if db_module := course.get_module(chapter.name):
            db_module.update(**fields)
        else:
            db_module = db.Module(**fields)

        return db_module

    def _load_lesson(
        self, course_id: int, module_id: int, index: int, lesson: models.Lesson
    ) -> db.Lesson:
        fields = dict(
            course_id=course_id,
            module_id=module_id,
            name=lesson.name,
            title=lesson.title,
            content=lesson.content,
            index_=index)

        module = db.Module.find(id=module_id)
        assert module is not None

        if db_lesson := module.get_lesson(lesson.name):
            db_lesson.update(**fields)
        else:
            db_lesson = db.Lesson(**fields)

        return db_lesson

    def _load_author(
        self, author: models.Author
    ) -> db.Instructor:
        fields = dict(
            key=author.key,
            name=author.name,
            about=author.about,
        )

        if db_instructor := db.Instructor.find(key=author.key):
            db_instructor.update(**fields)
        else:
            db_instructor = db.Instructor(**fields)

        db_instructor.save()
        self._set_instructor_photo(db_instructor, author.photo)

        return db_instructor

    def _set_instructor_photo(
        self,
        instructor: db.Instructor,
        on_disk_photo: Optional[Union[FilePath, HttpUrl]],
    ) -> Optional[db.Asset]:
        if on_disk_photo is None:
            instructor.photo_path = None
            instructor.save()
            return None

        filename = on_disk_photo.name
        asset = instructor.get_asset(filename) or instructor.new_asset(filename)
        asset.save_file(on_disk_photo)

        instructor.photo_path = asset.get_url()
        instructor.save()

        return asset

    def _load_lesson_outline(
        self,
        course_id: int,
        module_id: int,
        lesson_id: int,
        module_index: int,
        lesson_index: int,
    ) -> db.CourseOutline:
        return db.CourseOutline(
            course_id=course_id,
            module_id=module_id,
            lesson_id=lesson_id,
            module_index=module_index,
            lesson_index=lesson_index,
        )

    def _load_outline(
        self, lesson_outlines: List[db.CourseOutline]
    ) -> List[db.CourseOutline]:
        for prev, this, next_ in iter_prevnext(lesson_outlines):
            this.prev_lesson_id = prev and prev.lesson_id or None
            this.prev_lesson_index = prev and prev.lesson_index or None

            this.next_lesson_id = next_ and next_.lesson_id or None
            this.next_lesson_index = next_ and next_.lesson_index or None

        return lesson_outlines


def iter_prevnext(ls: List[Any]) -> Iterator[Tuple[Any, Any, Any]]:
    if not ls:
        yield from ()  # empty iterator

    ls = [None, *ls, None]
    a, b, c = tee(ls, 3)
    next(b), next(c), next(c)

    for next_ in c:
        prev, this = next(a), next(b)
        yield prev, this, next_
