from pathlib import Path

import pytest
from pydantic import ValidationError

from riyaz import cli


def get_config_path(case):
    return Path(__file__).parent / "data" / f"{case}_config.yml"


def test_read_config():
    path = get_config_path("ok")

    config = cli.read_config(path)

    assert config.name == "sample-course"
    assert config.title == "Sample Course"

    assert config.authors == ["alfa", "bravo"]

    # check that newlines are preserved for markdown syntax in description
    assert "\n\n```python\nimport sample\n```\n" in config.description

    assert len(config.outline) == 2
    assert isinstance(config.outline[0], cli.Chapter)


def test_read_config_when_authors_type_is_incorrect():
    path = get_config_path("incorrect_authors")

    with pytest.raises(ValidationError):
        cli.read_config(path)


def test_read_config_when_chapters_type_is_incorrect():
    path = get_config_path("incorrect_chapters")

    with pytest.raises(ValidationError):
        cli.read_config(path)
