from pathlib import Path

import pytest
from pydantic import BaseModel, HttpUrl, validator

from riyaz.disk import read_config


def get_config_path(case):
    return Path(__file__).parent / "data" / f"{case}_config.yml"


@pytest.fixture
def disk_course():
    course_yml = get_config_path("ok")

    config = read_config(course_yml)
    return config


@pytest.fixture
def data_dir(request):
    return Path(request.fspath.dirname) / "data"
