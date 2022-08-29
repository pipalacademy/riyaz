from flask import Flask, abort, render_template, send_from_directory

import markdown
from typing import List

from . import config
from .db import Course, Store


# for plugins
stylesheet_urls: List[str] = []
javascript_urls: List[str] = []


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


@app.route("/api/courses/<name>/version")
def get_course_version(name: str):
    version = Store.get(name)
    status_code = 404 if version is None else 200
    response = {"version": version}

    return response, status_code


@app.route("/assets/<path:path>")
def serve_assets(path):
    return send_from_directory(config.assets_path, path)


@app.context_processor
def inject_plugins():
    return dict(
        javascript_urls=javascript_urls,
        stylesheet_urls=stylesheet_urls,
    )


# Plugin system

def include_javascript(url: str):
    javascript_urls.append(url)


def include_stylesheet(url: str):
    stylesheet_urls.append(url)


if __name__ == "__main__":
    # import plugins here to load them
    # example:
    # import feather_riyaz
    #
    # NOTE: not sure whether this works when app is served by gunicorn
    # or some other WSGI server. it depends on how they load it

    pass
