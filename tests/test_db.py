from riyaz import db

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

