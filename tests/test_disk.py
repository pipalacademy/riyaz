import os
import pytest
from pydantic import ValidationError

from riyaz import disk

from .conftest import get_config_path


@pytest.fixture
def change_workdir(monkeypatch, data_dir):
    monkeypatch.chdir(data_dir)


def test_read_config(change_workdir):
    path = get_config_path("ok")

    print(os.getcwd())

    config = disk.read_config(path)

    assert config.name == "sample-course"
    assert config.title == "Sample Course"

    assert config.authors == ["alfa", "bravo"]

    # check that newlines are preserved for markdown syntax in description
    assert "\n\n```python\nimport sample\n```\n" in config.description

    assert len(config.outline) == 2
    assert isinstance(config.outline[0], disk.DiskChapter)


def test_read_config_when_authors_type_is_incorrect(change_workdir):
    path = get_config_path("incorrect_authors")

    with pytest.raises(ValidationError):
        disk.read_config(path)


def test_read_config_when_chapters_type_is_incorrect(change_workdir):
    path = get_config_path("incorrect_chapters")

    with pytest.raises(ValidationError):
        disk.read_config(path)


def test_course_from_directory(data_dir):
    course = disk.get_course_from_directory(data_dir)
    assert course.name == "sample-course"
