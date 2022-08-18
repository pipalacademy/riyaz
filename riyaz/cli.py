"""
Documentation for Riyaz CLI

The CLI can run these commands:
    - `riyaz serve`: Start a local instance of Riyaz. Useful for local course
                     development
    - `riyaz new`: Start a new Riyaz course with the default template
    - `riyaz push`: Push the Riyaz course in current directory to a remote
                    server
    - `riyaz pull`: Pull a Riyaz course from a remote server
"""

import os
import re
from pathlib import Path
from typing import List, IO, Optional, Union

import click
import frontmatter
import yaml
from pydantic import BaseModel, HttpUrl, validator
from pydantic.types import FilePath


class ChapterConfig(BaseModel):
    name: str
    title: str
    lessons: List[FilePath]


class Config(BaseModel):
    name: str
    title: str
    short_description: Optional[str]
    description: str
    authors: List[str]
    outline: List[ChapterConfig]

    @validator("authors", each_item=True)
    def check_author_file_exists(cls, v):
        author_file = get_author_file_path(v)
        if not author_file.exists():
            raise ValueError(f"author file {author_file} does not exist")

        return v


class Lesson(BaseModel):
    name: str
    title: str
    path: FilePath

    @classmethod
    def from_path(cls, path: FilePath) -> "Lesson":
        name = path.name.split(".", 1)[0]
        with open(path) as f:
            title = get_first_heading(f) or titlify(name)

        return cls(name=name, title=title, path=path)


class Chapter(BaseModel):
    name: str
    title: str
    lessons: List[Lesson]

    @classmethod
    def from_config(cls, ch_config: ChapterConfig) -> "Chapter":
        lessons = [Lesson.from_path(path) for path in ch_config.lessons]
        return cls(name=ch_config.name, title=ch_config.title, lessons=lessons)


class Author(BaseModel):
    key: str
    name: str
    about: Optional[str]
    photo: Optional[Union[HttpUrl, FilePath]]

    @classmethod
    def from_key(cls, key: str) -> "Author":
        path = get_author_file_path(key)
        fm = frontmatter.load(path)

        return cls(
            key=key,
            name=fm.get("name"),
            photo=fm.get("photo"),
            about=fm.content,
        )


class Course(BaseModel):
    config: Config
    authors: List[Author]
    outline: List[Chapter]

    @classmethod
    def from_config(cls, config: Config) -> "Course":
        authors = [Author.from_key(key) for key in config.authors]
        outline = [
            Chapter.from_config(ch_config) for ch_config in config.outline
        ]
        return Course(config=config, authors=authors, outline=outline)


@click.group()
def main():
    pass


@main.command()
def serve():
    click.echo("Serving")


def read_config(path: Union[str, os.PathLike]) -> Config:
    with open(path) as f:
        config_dict = yaml.safe_load(f)

    config = Config.parse_obj(config_dict)
    return config


def get_first_heading(f: IO) -> Optional[str]:
    heading_regex = re.compile(r"^(?:#{1,6})(.+)")

    for line in f:
        if m := heading_regex.match(line):
            return m.group(1).strip()

    return None


def titlify(s: str) -> str:
    to_replace = r"[-_(\s+)]"
    unsymbol = re.sub(to_replace, " ", s)
    return unsymbol.title()


def get_author_file_path(name: str) -> Path:
    return Path(f"authors/{name}.md")
