from riyaz.app import include_stylesheet, include_javascript
from riyaz import config


feather_config = getattr(config, "feather")


def get_modes():
    modes = feather_config.get("modes", ["python"])
    return modes


def get_stylesheets():
    return [
        "/static/feather/codemirror/lib/codemirror.css",
        "/static/feather/feather.css",
    ]


def get_javascripts():
    mode_js = "/static/feather/codemirror/mode/{mode}/{mode}.js"
    return [
        "/static/feather/jquery-3.6.0.min.js",
        "/static/feather/codemirror/lib/codemirror.js",
        "/static/feather/codemirror/addon/mode/simple.js",
        "/static/feather/codemirror/keymap/sublime.js",
        *[mode_js.format(mode=mode) for mode in get_modes()],
        "/static/feather/feather.js",
        "/static/feather/feather_config.js",
    ]


def inject_assets():
    stylesheets = get_stylesheets()
    javascripts = get_javascripts()

    for ss in stylesheets:
        include_stylesheet(ss)

    for js in javascripts:
        include_javascript(js)


inject_assets()
