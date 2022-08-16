from flask import Blueprint, abort, render_template

from functools import wraps

from .models import db


bp = Blueprint("courses", __name__)


@bp.route("/<name>")
def view_course(name: str):
    course = get_course(name=name)
    return render_template("course.html", course=course)


@bp.route("/<course_name>/<module_name>/<lesson_name>")
def view_lesson(course_name: str, module_name: str, lesson_name: str):
    course = get_course(name=course_name)
    lesson = get_lesson(
        course_id=course.id,
        module_name=module_name,
        lesson_name=lesson_name,
    )

    return render_template("lesson.html", course=course, lesson=lesson)


def abort_if_none(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        retval = fn(*args, **kwargs)
        if retval is None:
            abort(404)

        return retval

    return wrapper


@abort_if_none
def get_course(name):
    course = db.get("course", name)
    return course


@abort_if_none
def get_lesson(course_id: str, module_name: str, lesson_name: str):
    return db.get("lesson", f"{module_name}/{lesson_name}")
