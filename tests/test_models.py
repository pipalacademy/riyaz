import pytest


@pytest.fixture(autouse=True)
def change_workdir(monkeypatch, data_dir):
    monkeypatch.chdir(data_dir)


def test_get_course(model_course):
    course = model_course

    assert len(course.authors) == 2
    assert len(course.outline) == 2

    assert (
        course.outline[0].lessons[1].content.strip("\n")
        == "### something more about sample"
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
