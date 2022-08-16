# riyaz

Toolkit to create interactive courses with live coding examples and exercises.

## How to use

This software requires sqlite 3.38.0 or higher.

Step 1: Setup database

```
$ sqlite3 riyaz.db < riyaz/schema.sql
```

Step 2: install python dependencies

```
$ pip install -r requirements.txt dev-requirements.txt
```

Step 3: run the app

```
$ FLASK_APP=riyaz.app:app flask run
```





