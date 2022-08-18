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
from typing import List, Optional, Union

import click
import yaml
from pydantic import BaseModel


class Chapter(BaseModel):
    name: str
    title: str
    lessons: List[str]


class Config(BaseModel):
    name: str
    title: str
    short_description: Optional[str]
    description: str
    authors: List[str]
    outline: List[Chapter]


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
