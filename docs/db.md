# The Database

Riyaz uses a document database built-on top of sqlite. It is built to simplify the development of the application, taking care of most of the CRUD operations and providing a simple API to store and retrive the data used by the application.

## Concepts

**Document**: The database stores documents. Each document is of a particular type, is idenfied by its `fqn`, the fully qualified name, will have multiple fields as key-value pairs.

**Type**: Every document in the db is of a particular type and the allowed fields for the document and other constraints are specified in the schema of the type.
## Document

Each document in the Riyaz db will have the following fields.

**type**<br>
The type of the document - must be one of the user defined types

**parant** _readonly_<br>
The reference to the parent document. This could be empty/null. This is a read-only field derived from the field that is marked as parent in the schema of the type.

**key**<br>
Key to identify the document. The combination of (type, parent, key) is unique in the system.

**fqn** _readonly_<br>
the fully qualified name of the document. This is a read-only field and the value will be `{parent}:{key}`.

**uuid** _readonly_<br>
uuid to uniquely identify this document. This is generated when the document is created and can not be changed.

**created** _readonly_<br>
The timestamp of the creation time of the document. This never changes after the document is created.

**last_modified** _readonly_<br>
The timestamp of the last modified time of the document. This is updated to the current timestamp every time the document is updated.

In addition to these common fields, every document will have fields defined in the schema of it's type.

Here are a couple examples of documents written in yaml to make it easier to read.

```
type: course
key: python-primer
parent: null
fqn: python-primer
created: 2022-01-01 10:20:30
last_modified: 2022-02-02 11:22:33

title: Python Primer
short_description: Learn Python in 24 hours
description: Python Primer is ...
outline: ...
---
type: lesson
key: getting-started
parent: python-primer
fqn: "python-primer:getting-started"
created: 2022-01-01 10:20:30
last_modified: 2022-02-02 11:22:33

title: Getting Started
content: ...
```

## Schema

The schema of a type defines the fields a document of that type can have, their types and other constraints.

A schema is a list of fields and each field will have the following properties:

- name: name of the field
- type: type of the field - this could be one of the system types or a user defined type
- list: optional boolean value indicating if this field supports multiple values
- parent: optional boolean value indicating that this field defines the parent namespace for this document.

The following are the system defined types.

- int: an integer
- float: a real number
- boolean: `true` or `false`
- string: simple text, typically a single-line text
- markdown: text in markdown format
- image: an attached image
- file: an attached file
- object: any data

The following is an example of a schema:

```
type: type
name: course
fields:
- name: title
  type: string
- name: short_description
  type: string
- name: description
  type: markdown
- name: instructors
  type: instructor
  list: true
- name: outline
  type: object
```

It specifies that the `instructors` field is of type `instructor` and is a list of values instead of single value.

The `outline` is of type `object` indicating that it can have any value. The database will not do any validations on what is inside this and it is the application's responsibility to ensure the data integrety of this field.

How to specify the schema is not yet decided. One option is to specify it as yaml file as shown in the example above and another option is to define it in Python as shown below:

```
class Course(Type):
    title = Field(type="string")
    short_description = Field(type="string")
    description = Field(type="markdown")
    authors = Field(type="author", list=True)

class Lesson(Type):
    course = Field(type="course", parent=True)
    title = Field(type="string")
    content = Field(type="markdown")
```

As you can see in the Lesson type, the `course` field is marked as parent, so the `fqn` of a lesson will be generated automatically by joining the `course` field and the `key` field.

## The Interface

The db module provides the following interface to interact with the database.

```python
def get(type_, fqn=None, key=None, parent=None):
    """Returns the document with given fqn or key.
    """
    ...

def get_many(type_, keys):
    """Returns the documents with matching keys.

    [or should this be fqns?]
    """
    ...

def query(type_, **q):
    """Returns all the documents matching the given query.

        >>> query("course", title="Foo")
        ...
    """
    ...
```

## Open Issues

* Is supporting hierarchy with seperating `parent` and `key` and autogeneraitng `fqn` is making the db interface complex? Are we better off not supporting the hierarchy? Any other ways to achieve the same?

* The db allows two documents of different type to have same `fqn`. It may be a good idea to make the `fqn` truly unique, even across types.

