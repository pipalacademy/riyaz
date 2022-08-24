import pytest

from riyaz.disk import read_config


class TestGetCourse:
    @pytest.fixture(autouse=True)
    def change_workdir(self, monkeypatch, course_dir):
        self.course_dir = course_dir
        monkeypatch.chdir(course_dir)

    @pytest.fixture
    def disk_course(self):
        return read_config(self.course_dir / "course.yml")

    def test_get_course(self, disk_course):
        course = disk_course.parse()

        assert len(course.authors) == 1
        assert len(course.outline) == 1
        assert len(course.outline[0].lessons) == 2

        for module in course.outline:
            assert module.name is not None
            assert module.title is not None
            for lesson in module.lessons:
                for key in ["content", "title", "name"]:
                    assert getattr(lesson, key, None) is not None

        author = course.authors[0]
        assert author.key == "alice"
        assert author.name == "Alice"
        assert author.about is not None
        assert author.photo is None
