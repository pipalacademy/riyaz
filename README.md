# riyaz

Riyaz is a light-weight, self-hostable learning platform.

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

Step 3: load sample data

```
$ python run.py --load-sample-data
```

Step 4: run the app

```
$ python run.py
```





