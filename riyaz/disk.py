"""
pydantic models and utility functions for parsing the on-disk courses go here.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Union

import yaml
from pydantic import BaseModel, validator
from pydantic.types import FilePath


class DiskChapter(BaseModel):
    name: str
    title: str
    lessons: List[FilePath]


class DiskCourse(BaseModel):
    name: str
    title: str
    short_description: Optional[str]
    description: str
    authors: List[str]
    outline: List[DiskChapter]

    @validator("authors", each_item=True)
    def check_author_file_exists(cls, v):
        author_file = get_author_file_path(v)
        if not author_file.exists():
            raise ValueError(f"author file {author_file} does not exist")

        return v


def read_config(path: Union[str, os.PathLike]) -> DiskCourse:
    with open(path) as f:
        config_dict = yaml.safe_load(f)

    return DiskCourse.parse_obj(config_dict)


def get_author_file_path(name: str) -> Path:
    return Path(f"authors/{name}.md")
