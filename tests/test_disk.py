import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError

from riyaz import disk


def get_config_path(base):
    return Path(base / "course.yml")


class TestReadConfig:
    @pytest.fixture
    def ok_config_path(self, course_dir):
        config_path = get_config_path(course_dir)
        return config_path

    @pytest.fixture
    def incorrect_authors_config_path(self, course_dir):
        config_path = get_config_path(course_dir)

        with open(config_path, "r+") as f:
            data = yaml.safe_load(f)
            data.update(authors="alice")  # str instead of list
            yaml.dump(data, f)

        return config_path

    @pytest.fixture
    def incorrect_chapters_config_path(self, course_dir):
        config_path = get_config_path(course_dir)

        with open(config_path, "r+") as f:
            data = yaml.safe_load(f)
            data["outline"][0].pop("title")  # no title (required field)
            yaml.dump(data, f)

        return config_path

    def test_read_config(self, ok_config_path):
        config = disk.read_config(ok_config_path)

        assert config.name == "hello-world"
        assert config.title == "Hello, World!"

        assert config.authors == ["alice"]

        # check that newlines are preserved for markdown syntax in description
        assert "\n\n```python\nimport sample\n```\n" in config.description

        assert len(config.outline) == 1
        assert len(config.outline[0].lessons) == 2
        assert isinstance(config.outline[0], disk.DiskChapter)


    def test_read_config_when_authors_type_is_incorrect(self, incorrect_authors_config_path):
        with pytest.raises(ValidationError):
            disk.read_config(incorrect_authors_config_path)


    def test_read_config_when_chapters_type_is_incorrect(self, incorrect_chapters_config_path):
        with pytest.raises(ValidationError):
            disk.read_config(incorrect_chapters_config_path)


def test_course_from_directory(course_dir):
    course = disk.get_course_from_directory(course_dir)
    assert course.name == "hello-world"
