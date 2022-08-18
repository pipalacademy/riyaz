from pathlib import Path

import os
import pytest
from pydantic import ValidationError

from riyaz import cli


@pytest.fixture(autouse=True)
def change_workdir(request, monkeypatch):
    monkeypatch.chdir(Path(request.fspath.dirname) / "data")


def get_config_path(case):
    return Path(__file__).parent / "data" / f"{case}_config.yml"


def test_read_config():
    path = get_config_path("ok")

    print(os.getcwd())

    config = cli.read_config(path)

    assert config.name == "sample-course"
    assert config.title == "Sample Course"

    assert config.authors == ["alfa", "bravo"]

    # check that newlines are preserved for markdown syntax in description
    assert "\n\n```python\nimport sample\n```\n" in config.description

    assert len(config.outline) == 2
    assert isinstance(config.outline[0], cli.ChapterConfig)


def test_read_config_when_authors_type_is_incorrect():
    path = get_config_path("incorrect_authors")

    with pytest.raises(ValidationError):
        cli.read_config(path)


def test_read_config_when_chapters_type_is_incorrect():
    path = get_config_path("incorrect_chapters")

    with pytest.raises(ValidationError):
        cli.read_config(path)


def test_get_course():
    course_yml = get_config_path("ok")

    config = cli.read_config(course_yml)
    course = cli.Course.from_config(config)

    assert len(course.authors) == 2
    assert len(course.outline) == 2

    assert (
        str(course.outline[0].lessons[1].path)
        == "getting-started/more-about-sample.md"
    )
    assert course.outline[0].lessons[0].title == "How To Use Sample"

    assert course.outline[1].lessons[0].name == "more-use-cases-of-sample"
    assert course.outline[1].lessons[0].title == "Use cases of Sample"

    alfa_author = course.authors[0]
    assert alfa_author.key == "alfa"
    assert alfa_author.name == "Alfa"
    assert alfa_author.photo is None
    assert (
        alfa_author.about.strip()
        == "Alfa is a good person who can write in *italics* and `code`."
    )

    bravo_author = course.authors[1]
    assert bravo_author.key == "bravo"
    assert bravo_author.name == "Bravo Bob"
    assert bravo_author.photo == "https://example.com"
    assert bravo_author.about.strip() == "Bravo"
