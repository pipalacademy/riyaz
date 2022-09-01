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
import sys
import tempfile
from pathlib import Path

import click
import yaml
from cookiecutter.main import cookiecutter

from riyaz import config
from riyaz.app import app
from riyaz.disk import CourseLoader
from riyaz.migrate import migrate
from .livereload import live_reload


class fmt:
    error_style = {"fg": "red", "bold": True}
    success_style = {"fg": "green", "bold": True}

    @classmethod
    def error(cls, message, exit=False, exit_code=1):
        click.echo(click.style(message, **cls.error_style))
        if exit:
            sys.exit(exit_code)

    @classmethod
    def success(cls, message):
        click.echo(click.style(message, **cls.success_style))


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

    with tempfile.TemporaryDirectory(prefix="riyaz_") as tempdir:
        setup_db(tempdir)
        setup_assets(tempdir)

        loader.load()
        with live_reload(loader, course_dir):
            app.run()


@main.command(short_help="setup a new course from template")
def new():
    """Setup a new Riyaz course from default template.
    """
    template_path = Path(__file__).parent.parent / "cookiecutter-course/"
    cookiecutter(str(template_path))


@main.command(short_help="create a directory for persistent deployment")
@click.argument("path", type=click.Path(path_type=Path))
def new_site(path):
    """Create a new Riyaz site at PATH.

    PATH is a path to a directory that will be created. This directory
    shouldn't exist prior to invoking this command.

    This directory will store data needed for a persistent Riyaz deployment,
    like database, configuration, and assets.
    This can be used to host multiple courses and persist state through
    restarts.

    \b
    Example usage:
    ```
    $ riyaz new-site riyaz-prod
    New Riyaz site created at riyaz-prod.
    $ ls riyaz-prod/
    assets riyaz.db riyaz.yml
    ```

    \b
    To start the server, cd into the site directory and start a WSGI server
    with entrypoint `riyaz.app:app`.
    ```
    $ cd riyaz-prod
    $ gunicorn riyaz.app:app
    Starting web server ...
    ```
    """
    if path.exists():
        fmt.error(f"Directory {path} already exists", exit=True)

    path.mkdir()
    setup_db(path)
    setup_assets(path)
    setup_config(path)

    fmt.success(f"New Riyaz site created at {path}")


@main.command("import-course")
@click.option("-s", "--site", default=Path("."), show_default=True,
              type=click.Path(path_type=Path))
@click.argument("course_dir", type=click.Path(path_type=Path))
def import_course(site, course_dir):
    if not site.is_dir():
        fmt.error(f"'{site}' is not a directory", exit=True)

    if not course_dir.is_dir():
        fmt.error(f"'{course_dir}' is not a directory", exit=True)

    # set configuration - database_path, assets_path
    config.load_config(site / "riyaz.yml")
    course = CourseLoader(course_dir).load()

    fmt.success(f"Successfully loaded course '{course.title}'")


def setup_db(base_dir):
    config.database_path = os.path.join(base_dir, "riyaz.db")
    migrate()


def setup_assets(base_dir):
    config.assets_path = os.path.join(base_dir, "assets")
    os.makedirs(config.assets_path, exist_ok=True)


def setup_config(base_dir):
    config_path = os.path.join(base_dir, "riyaz.yml")
    initial_config = {
        "database_path": "riyaz.db",
        "assets_path": "assets",
    }

    with open(config_path, "w") as f:
        yaml.safe_dump(initial_config, f)
