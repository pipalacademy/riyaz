"""
pydantic models that we use for APIs will go here.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel
from pydantic.types import FilePath


class Lesson(BaseModel):
    name: str
    title: str
    content: str


class Chapter(BaseModel):
    name: str
    title: str
    lessons: List[Lesson]


class Author(BaseModel):
    key: str
    name: str
    about: Optional[str]
    photo: Optional[FilePath]


class Course(BaseModel):
    name: str
    title: str
    short_description: Optional[str]
    description: str
    authors: List[Author]
    outline: List[Chapter]
