"""
pydantic models and utility functions for parsing the on-disk courses go here.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

import frontmatter
import yaml
from pydantic import BaseModel, validate_arguments, validator
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
            self._load_author(idx, author)
            for idx, author in enumerate(parsed_course.authors)
        ]
        course.set_instructors(*instructors)

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

        return course

    def _load_course(self, course: models.Course) -> db.Course:
        return db.Course(
            key=course.name,
            title=course.title,
            short_description=course.short_description,
            description=course.description,
        )

    def _load_chapter(
        self, course_id: int, index: int, chapter: models.Chapter
    ) -> db.Module:
        return db.Module(
            course_id=course_id,
            name=chapter.name,
            title=chapter.title,
            index_=index,
        )

    def _load_lesson(
        self, course_id: int, module_id: int, index: int, lesson: models.Lesson
    ) -> db.Lesson:
        return db.Lesson(
            course_id=course_id,
            module_id=module_id,
            name=lesson.name,
            title=lesson.title,
            content=lesson.content,
            index_=index,
        )

    def _load_author(
        self, course_id: int, author: models.Author
    ) -> db.Instructor:
        return db.Instructor(
            course_id=course_id,
            key=author.key,
            name=author.name,
            about=author.about,
            photo_path=author.photo,
        )
