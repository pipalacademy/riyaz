# Riyaz Database

Riyaz uses a simple schema-less, document database built on top of sqlite.

The database is schema-less and it does not do any data integrity checks. The responsibility of data integraty is completely with the application using the database.

## Concepts

The database is a collection of documents and each document contains three fields doctype, key and data.

```
Document:
- doctype: str
- key: str
- data: dict
```

In addition to these fields, the database also maintains an `id` field which is used only for internal use.


## Usage

The db module provides a base `Document` class.

Here is the sample usage.

```
one = Document("one", {"value": 1, "square": 1, "parity": "odd"}).save()
two = Document("two", {"value": 2, "square": 4, "parity": "even"}).save()
three = Document("three", {"value": 3, "square": 9, "parity": "odd"}).save()

doc = Document.find(key="one")
print(doc.key, doc.value) # one 1

doc = Document.find(square=4)
print(doc.key, doc.value) # two 2

doc = Document.find_all()
keys = [doc.key for doc in docs]
print(keys) # ['one', 'two', 'three']

doc = Document.find_all(parity='odd')
keys = [doc.key for doc in docs]
print(keys) # ['one', 'three']
```

Please note that the fields in the `data` can be accessed directly from the `doc`. For example `doc.value` will give the value of `doc.data['value']`.

## Models

The db module supports creating your own model class for each doctype.

For example, the following code creates a new model class for doctype `number`.

```
from riyaz.db import Document, register_model

class Number(Document):
    DOCTYPE = "number"

register_model(Number)

one = Number("one", {"value": 1, "square": 1, "parity": "odd"}).save()
two = Number("two", {"value": 2, "square": 4, "parity": "even"}).save()
three = Number("three", {"value": 3, "square": 9, "parity": "odd"}).save()

doc = Number.find(key="one")
print(doc.key, doc.value) # one 1
print(doc.doctype) # number
print(type(doc)) # Number

doc = Number.find(square=4)
print(doc.key, doc.value) # two 2

doc = Number.find_all()
keys = [doc.key for doc in docs]
print(keys) # ['one', 'two', 'three']

doc = Number.find_all(parity='odd')
keys = [doc.key for doc in docs]
print(keys) # ['one', 'three']
```

## Pros and Cons

The following are the pros and cons of using this database.

**Pros:**

- Very easy to use
- supports nested data
- very simple query interface

**Cons**

- supports limited ways to query - for example, it is not possible use `OR` clause in queries
- no way to do joins
- no way to do count(*) queries and group by
- not possible to write raw sql

