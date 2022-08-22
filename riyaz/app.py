from flask import Flask, abort, render_template

import markdown

from .doctypes import Course


app = Flask("riyaz")


@app.template_filter("markdown")
def md_to_html(md: str):
    return markdown.markdown(md, extensions=["fenced_code"])


@app.route("/")
def index():
    courses = Course.find_all()
    return render_template("index.html", courses=courses)


@app.route("/courses/<name>")
def view_course(name: str):
    course = Course.find(key=name)
    if not course:
        abort(404)

    return render_template("course.html", course=course)


@app.route("/courses/<course_name>/<module_name>/<lesson_name>")
def view_lesson(course_name: str, module_name: str, lesson_name: str):
    course = Course.find(key=course_name)
    lesson = course and course.get_lesson(module_name, lesson_name)
    if not lesson:
        abort(404)

    return render_template("lesson.html", course=course, lesson=lesson)
