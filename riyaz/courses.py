from flask import Blueprint, render_template


bp = Blueprint("courses", __name__)


@bp.route("/<name>")
def view_course(name: str):
    course = get_course(name=name)
    return render_template("course.html", course=course)


def get_course(name):
    return {
        "id": "a1afe86d-8a99-489e-b3f8-7d2be764a857",
        "name": "alpha-course",
        "title": "Alpha Course",
        "short_description": "A course on Alpha",
        "description": """\
This is a description of the **Alpha Course**. It is a *course
about Alpha*. `Alpha` is very useful.

You can use it like:

```
import alpha

alpha.alpha("hello, world")
```
        """,
        "authors": [
            {
                "id": "ab8bcec7-b384-46b6-b496-0d6df4615a3e",
                "name": "Alice",
                "photo": "https://thispersondoesnotexist.com/image",
            },
            {
                "id": "84517dac-33af-4cb7-8dff-7acc1fadb360",
                "name": "Chuck",
                "photo": "https://thispersondoesnotexist.com/image",
            },
        ],
    }
