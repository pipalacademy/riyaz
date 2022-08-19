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
from pathlib import Path

import click

from riyaz import models
from riyaz import doctypes
from riyaz.app import app
from riyaz.migrate import migrate
from riyaz.sample_data import load_sample_data


@click.group()
def main():
    pass


@main.command()
def serve():
    setup_db()
    app.run()


def setup_db():
    migrate()
    sample_data_path = Path(__file__).parent.parent.resolve() / "sample_data"
    print("sample_data", sample_data_path)
    print("contents: ", [p for p in sample_data_path.glob("*")])
    load_sample_data(sample_data_path)

    workdir = Path.cwd()
    course_model = models.Course.from_directory(workdir)
    course = doctypes.Course.save_from_model(course_model)
    print("course", course.name, course.title)
