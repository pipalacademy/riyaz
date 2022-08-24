import shutil
import tempfile
from pathlib import Path

import pytest
from pydantic import BaseModel, HttpUrl, validator

from riyaz.disk import read_config


sample_course_name = "hello-world"
sample_course_dir = (
    Path(__file__).parent.parent / "sample_courses" / sample_course_name
)


@pytest.fixture
def course_dir(request):
    with tempfile.TemporaryDirectory(prefix="test_riyaz_") as tempdir:
        dest = Path(tempdir) / sample_course_name
        shutil.copytree(sample_course_dir, dest)
        yield dest


@pytest.fixture
def disk_course(course_dir):
    course_yml = course_dir / "course.yml"

    config = read_config(course_yml)
    return config
