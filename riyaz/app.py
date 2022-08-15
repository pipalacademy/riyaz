from flask import Flask, render_template

from . import courses


app = Flask("riyaz")
app.register_blueprint(courses.bp, url_prefix="/courses")


@app.route("/")
def index():
    placeholder_courses = [
        {
            "id": "a1afe86d-8a99-489e-b3f8-7d2be764a857",
            "name": "alpha-course",
            "title": "Alpha Course",
            "short_description": "A course on Alpha",
            "authors": [
                {
                    "id": "ab8bcec7-b384-46b6-b496-0d6df4615a3e",
                    "name": "Alice",
                    "photo": "https://thispersondoesnotexist.com/image",
                }
            ],
        },
        {
            "id": "d7965fec-a530-4cb3-b739-3ce074145bce",
            "name": "bravo-course",
            "title": "Bravo Course",
            "short_description": "A course on Bravo",
            "authors": [
                {
                    "id": "b576389e-74d7-46fe-8019-e0262a1ea35c",
                    "name": "Bob",
                    "photo": "https://thispersondoesnotexist.com/image",
                }
            ],
        },
        {
            "id": "e86948f5-5593-430b-966d-3cf611870db4",
            "name": "charlie-course",
            "title": "Charlie Course",
            "short_description": "A course on Charlie",
            "authors": [
                {
                    "id": "84517dac-33af-4cb7-8dff-7acc1fadb360",
                    "name": "Chuck",
                    "photo": "https://thispersondoesnotexist.com/image",
                }
            ],
        },
    ]

    return render_template("index.html", courses=placeholder_courses)
