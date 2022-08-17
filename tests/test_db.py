from riyaz import db
import pytest

def setup_function():
    with db.get_connection() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM document")

def test_save():
    assert db.get("number", "one") is None
    db.save("number", "one", {"name": "One"})

    doc = db.get("number", "one")
    assert doc.id is not None
    assert doc.name == "One"

    db.save("number", "one", {"name": "Uno"})
    doc2 = db.get("number", "one")
    assert doc2.id == doc.id
    assert doc2.name == "Uno"

def test_get():
    assert db.get("number", "one") is None

    db.save("document", "one", {"name": "Document One"})
    assert db.get("number", "one") is None

    db.save("number", "one", {"name": "One", "value": 1})
    doc = db.get("number", "one")
    assert doc is not None
    assert doc.data == {"name": "One", "value": 1}



def test_get_many():
    db.save("number", "one", {"name": "One"})
    db.save("number", "two", {"name": "Two"})
    db.save("number", "three", {"name": "Three"})

    docs = db.get_many("number", ['one', 'two'])
    keys = [doc.key for doc in docs]
    assert keys == ['one', 'two']

    docs = db.get_many("number", ['two', 'one'])
    keys = [doc.key for doc in docs]
    assert keys == ['two', 'one']

def test_query():
    for n in range(10):
        parity = ["even", "odd"][n%2]
        data = {
            "n": n,
            "parity": parity,
            "multiple_of_3": n % 3 == 0
        }
        db.save("number", str(n), data)

    db.save("document", "foo", {})
    db.save("document", "bar", {})

    docs = db.query("number")
    keys = sorted([doc.key for doc in docs])
    assert keys == ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    docs = db.query("number", parity='even')
    keys = [doc.key for doc in docs]
    assert keys == ['0', '2', '4', '6', '8']

    docs = db.query("number", parity='odd')
    keys = [doc.key for doc in docs]
    assert keys == ['1', '3', '5', '7', '9']

    docs = db.query("number", parity='odd', multiple_of_3=True)
    keys = [doc.key for doc in docs]
    assert keys == ['3', '9']

def test_Document_save():
    class Number(db.Document):
        DOCTYPE = "number"

    Number("one", {"value": 1}).save()
    doc = Number.find(key="one")
    assert doc is not None
    assert doc.value == 1

def test_Document_find():
    class Number(db.Document):
        DOCTYPE = "number"

    Number("one", {"value": 1, "square": 1}).save()
    Number("two", {"value": 2, "square": 4}).save()

    doc = Number.find(key="one")
    assert doc is not None
    assert doc.value == 1

    doc = Number.find(square=4)
    assert doc is not None
    assert doc.key == "two"
    assert doc.value == 2

    assert Number.find(key="three") is None
    assert Number.find(square=9) is None

def test_Document_find_all():
    class Number(db.Document):
        DOCTYPE = "number"

    Number("one", {"value": 1, "parity": "odd"}).save()
    Number("two", {"value": 2, "parity": "even"}).save()
    Number("three", {"value": 3, "parity": "odd"}).save()
    Number("four", {"value": 4, "parity": "even"}).save()

    # having a db.Document with the same key should not alter our results
    db.Document("one", {"value": 1, "parity": "odd"}).save()

    docs = Number.find_all()
    keys = {doc.key for doc in docs}
    assert keys == {'one', 'two', 'three', 'four'}

    docs = Number.find_all(parity='odd')
    keys = {doc.key for doc in docs}
    assert keys == {'one', 'three'}

    docs = Number.find_all(parity='even')
    keys = {doc.key for doc in docs}
    assert keys == {'two', 'four'}

    docs = Number.find_all(parity='strange')
    keys = {doc.key for doc in docs}
    assert keys == set()

def test_Document_getattr():
    doc = db.Document("one", {"value": 1}).save()
    print("doc", doc.__dict__)
    assert doc.id is not None
    assert doc.value == 1

    # test for issue #12
    with pytest.raises(AttributeError) as e:
        doc._foo

    assert str(e.value) == '_foo'
