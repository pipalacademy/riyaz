"""
pydantic models that we use for APIs will go here.
"""
from __future__ import annotations

import re
from typing import List, Optional, Union

import frontmatter
from pydantic import BaseModel, HttpUrl
from pydantic.types import FilePath

from .disk import DiskChapter, DiskCourse, get_author_file_path


class Lesson(BaseModel):
    name: str
    title: str
    content: str

    @classmethod
    def from_path(cls, path: FilePath) -> Lesson:
        name = path.name.split(".", 1)[0]
        with open(path) as f:
            content = f.read()
            title = get_first_heading(content) or titlify(name)

        return cls(name=name, title=title, content=content)


class Chapter(BaseModel):
    name: str
    title: str
    lessons: List[Lesson]

    @classmethod
    def from_disk(cls, disk_chapter: DiskChapter) -> Chapter:
        lessons = [Lesson.from_path(path) for path in disk_chapter.lessons]
        return cls(
            name=disk_chapter.name, title=disk_chapter.title, lessons=lessons
        )


class Author(BaseModel):
    key: str
    name: str
    about: Optional[str]
    photo: Optional[Union[HttpUrl, FilePath]]

    @classmethod
    def from_key(cls, key: str) -> Author:
        path = get_author_file_path(key)
        fm = frontmatter.load(path)

        return cls(
            key=key,
            name=fm.get("name"),
            photo=fm.get("photo"),
            about=fm.content,
        )


class Course(BaseModel):
    config: DiskCourse
    authors: List[Author]
    outline: List[Chapter]

    @classmethod
    def from_config(cls, config: DiskCourse) -> Course:
        authors = [Author.from_key(key) for key in config.authors]
        outline = [
            Chapter.from_disk(disk_chapter) for disk_chapter in config.outline
        ]
        return Course(config=config, authors=authors, outline=outline)


def get_first_heading(content: str) -> Optional[str]:
    heading_regex = re.compile(r"^(?:#{1,6})(.+)", re.MULTILINE)

    if m := heading_regex.search(content):
        return m.group(1).strip()

    return None


def titlify(s: str) -> str:
    to_replace = r"[-_(\s+)]"
    unsymbol = re.sub(to_replace, " ", s)
    return unsymbol.title()
