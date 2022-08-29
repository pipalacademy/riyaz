from flask import (
    Flask, abort, render_template, send_from_directory
)

import importlib
import markdown
from typing import List

from . import config
from .db import Course, Store


app = Flask("riyaz")

javascript_urls: List[str] = []
stylesheet_urls: List[str] = []
plugins: List[str] = [
    # "feather.riyaz_plugin",
]


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


# plugins

@app.context_processor
def inject_plugins():
    return dict(
        javascript_urls=javascript_urls,
        stylesheet_urls=stylesheet_urls,
    )


@app.before_request
def load_plugins():
    for plugin_module in plugins:
        importlib.import_module(plugin_module)


def include_stylesheet(url):
    stylesheet_urls.append(url)


def include_javascript(url):
    javascript_urls.append(url)
