import pytest

from riyaz.doctypes import Course, Module, Lesson, db
from riyaz.migrate import migrate
from riyaz.sample_data import load_sample_data


def setup_function():
    migrate()
    load_sample_data("sample_data")


def teardown_function():
    with db.get_connection() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM document")


@pytest.fixture
def cd_data_dir(monkeypatch, data_dir):
    monkeypatch.chdir(data_dir)


@pytest.fixture
def course():
    return Course.find(key="alpha-course")


@pytest.fixture
def new_course():
    course = Course(
        "new-course",
        {
            "name": "new-course",
            "title": "New Course",
            "description": "hello world",
            "outline": [
                {
                    "name": "uno-module",
                    "title": "Uno Module",
                    "lessons": [
                        {"name": "onnu-lesson", "title": "Onnu Lesson"},
                        {"name": "naalu-lesson", "title": "Naalu Lesson"},
                    ],
                }
            ],
        },
    ).save()

    module = Module(
        "uno-module",
        {"course": course.key, "name": "uno-module", "title": "Uno Module"},
    ).save()

    Lesson(
        f"{module.key}/onnu-lesson",
        {
            "name": "onnu-lesson",
            "title": "Onnu Lesson",
            "content": "Hello world",
            "course": course.key,
            "module": module.key,
        },
    ).save()
    Lesson(
        f"{module.key}/naalu-lesson",
        {
            "name": "onnu-lesson",
            "title": "Naalu Lesson",
            "content": "Hello world 2",
            "course": course.key,
            "module": module.key,
        },
    ).save()

    return course


def test_course_get_lesson_ok(course):
    lesson = course.get_lesson("uno-module", "onnu-lesson")
    assert isinstance(lesson, Lesson)

    lesson = course.get_lesson("uno-module", "rendu-lesson")
    assert isinstance(lesson, Lesson)

    lesson = course.get_lesson("uno-module", "moonu-lesson")
    assert isinstance(lesson, Lesson)


def test_course_get_lesson_when_lesson_doesnt_exist(course):
    lesson = course.get_lesson("uno-module", "naalu-lesson")
    assert lesson is None


def test_course_get_lesson_when_lesson_is_in_a_different_course(
    course, new_course
):
    lesson = course.get_lesson("uno-module", "naalu-lesson")
    assert lesson is None


def test_course_get_lesson_when_lesson_with_same_name_exists_in_two_courses(
    course, new_course
):
    lesson = new_course.get_lesson("uno-module", "onnu-lesson")

    assert isinstance(lesson, Lesson)
    assert lesson.course == new_course.key


def test_course_get_module_index(course):
    module_i = course.get_module_index("uno-module")
    assert module_i == 1

    module_i = course.get_module_index("non-existent-module")
    assert module_i is None


def test_course_get_lesson_index(course):
    mod_lsn_i = course.get_lesson_index("uno-module", "moonu-lesson")
    assert mod_lsn_i == (1, 3)

    mod_lsn_i = course.get_lesson_index("uno-module", "naalu-lesson")
    assert mod_lsn_i is None


def test_course_get_next_lesson(course):
    lesson = course.get_lesson("uno-module", "onnu-lesson")
    next_lesson = course.get_next_lesson(lesson)
    assert isinstance(next_lesson, Lesson)
    assert next_lesson.module == "uno-module"
    assert next_lesson.name == "rendu-lesson"

    lesson = course.get_lesson("uno-module", "moonu-lesson")
    next_lesson = course.get_next_lesson(lesson)
    assert isinstance(next_lesson, Lesson)
    assert next_lesson.module == "dos-module"
    assert next_lesson.name == "naalu-lesson"

    lesson = course.get_lesson("dos-module", "moonu-lesson")
    next_lesson = course.get_next_lesson(lesson)
    assert next_lesson is None


def test_course_get_previous_lesson(course):
    lesson = course.get_lesson("uno-module", "onnu-lesson")
    previous_lesson = course.get_previous_lesson(lesson)
    assert previous_lesson is None

    lesson = course.get_lesson("uno-module", "moonu-lesson")
    previous_lesson = course.get_previous_lesson(lesson)
    assert isinstance(previous_lesson, Lesson)
    assert previous_lesson.module == "uno-module"
    assert previous_lesson.name == "rendu-lesson"

    lesson = course.get_lesson("dos-module", "naalu-lesson")
    previous_lesson = course.get_previous_lesson(lesson)
    assert isinstance(previous_lesson, Lesson)
    assert previous_lesson.module == "uno-module"
    assert previous_lesson.name == "moonu-lesson"


def test_save_from_model(cd_data_dir, model_course):
    Course.save_from_model(model_course)

    course = Course.find(key=model_course.name)
    assert isinstance(course, Course)
    assert course.name == model_course.name

    for module in model_course.outline:
        assert Module.find(key=module.name) is not None
        for lesson in module.lessons:
            assert course.get_lesson(module.name, lesson.name) is not None
