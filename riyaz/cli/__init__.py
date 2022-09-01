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
import sys
import tempfile
from pathlib import Path

import click
import yaml
from cookiecutter.main import cookiecutter
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from riyaz import config
from riyaz.app import app
from riyaz.disk import CourseLoader
from riyaz.migrate import migrate
from .livereload import live_reload


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
@click.argument("sitename", type=click.Path(path_type=Path))
def new_site(sitename):
    """Create a new Riyaz site at SITENAME.

    SITENAME is a path to a directory that will be created. This directory
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
    if sitename.exists():
        click.echo(click.style(
            f"Directory {sitename} already exists", fg="red", bold=True))
        sys.exit(1)

    sitename.mkdir()
    setup_db(sitename)
    setup_assets(sitename)
    setup_config(sitename)

    click.echo(click.style(
        f"New Riyaz site created at {sitename}", fg="green", bold=True))


@contextlib.contextmanager
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
