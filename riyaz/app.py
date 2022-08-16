from flask import Flask, render_template

import markdown

from . import courses
from .models import db


app = Flask("riyaz")
app.register_blueprint(courses.bp, url_prefix="/courses")


@app.route("/")
def index():
    courses = db.query("course")
    return render_template("index.html", courses=courses)


@app.template_filter("markdown")
def md_to_html(md: str):
    return markdown.markdown(md, extensions=["fenced_code"])
