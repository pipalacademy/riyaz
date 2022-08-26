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
import contextlib
import os
import tempfile
from pathlib import Path

import click
from cookiecutter.main import cookiecutter
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from riyaz import config
from riyaz.app import app
from riyaz.disk import CourseLoader
from riyaz.migrate import migrate
from .livereload import setup_livereload


@click.group()
def main():
    """
    Riyaz CLI tool to help with local development of courses.
    """
    pass


@main.command(short_help="start serving course from local directory")
def serve():
    """Start serving course from local directory

    Starts a live server that loads course from current directory,
    and watches for file changes to reload.
    """
    course_dir = Path.cwd()
    loader = CourseLoader(course_dir)

    with setup_db(), setup_livereload(loader=loader, path=course_dir):
        loader.load()
        app.run()


@main.command(short_help="setup a new course from template")
def new():
    """Setup a new Riyaz course from default template.
    """
    template_path = Path(__file__).parent.parent / "cookiecutter-course/"
    cookiecutter(str(template_path))


@contextlib.contextmanager
def setup_db():
    with tempfile.TemporaryDirectory(prefix="riyaz_") as tempdir:
        config.database_path = os.path.join(tempdir, "riyaz.db")
        migrate()

        yield


def reset_db():
    drop_db()
    migrate()


def drop_db():
    if os.path.exists(config.database_path):
        os.unlink(config.database_path)