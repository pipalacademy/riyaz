import pytest
import textwrap

from riyaz import db


class TestDocument:

    class Document_(db.Document):
        _TABLE = "testing_document"

        name: str
        text_: str

    migration_script = textwrap.dedent("""
    CREATE TABLE testing_document (
        id integer primary key,
        name text unique,
        text_ text
    );
    """)
    rollback_script = textwrap.dedent("""
    DROP TABLE testing_document;
    """)

    insert_rows_script = textwrap.dedent("""
    INSERT INTO testing_document (name, text_) VALUES
        ('first', 'this is first test value'),
        ('second', 'this is second test value');
    """)
    delete_rows_script = textwrap.dedent("""
    DELETE FROM testing_document;
    """)

    @pytest.fixture(scope="class", autouse=True)
    def migrate_and_rollback(self, get_db):
        cursor = get_db().ctx.db.cursor()

        cursor.execute(TestDocument.migration_script)
        yield
        cursor.execute(TestDocument.rollback_script)

    @pytest.fixture
    def populate_table(self, get_db):
        cursor = get_db().ctx.db.cursor()

        cursor.execute(TestDocument.insert_rows_script)
        yield
        cursor.execute(TestDocument.delete_rows_script)

    def test_document_find_all(self, populate_table):
        Document_ = self.__class__.Document_

        all_rows = Document_.find_all()
        assert len(all_rows) == 2

        filtered_rows = Document_.find_all(name="first")
        assert len(filtered_rows) == 1
        assert filtered_rows[0].text_ == "this is first test value"

        ordered_rows = Document_.find_all(order="name desc")
        assert ordered_rows[0].name == "second"

        empty_rows = Document_.find_all(name="doesnt-exist")
        assert len(empty_rows) == 0

    def test_document_find(self, populate_table):
        Document_ = self.__class__.Document_

        doc = Document_.find(name="first")
        assert doc is not None
        assert doc.name == "first" and doc.text_ == "this is first test value"

        doc = Document_.find(name="not-exist")
        assert doc is None

    def test_document_save(self):
        Document_ = self.__class__.Document_

        doc = Document_(name="third", text_="this is third test value")
        doc.save()
        assert Document_.find(name="third") is not None
        assert doc.id is not None

        doc = Document_(name="third", text_="this shouldn't save")
        with pytest.raises(Exception):
            doc.save()
        assert doc.id is None
        assert Document_.find(name="third").text_ != "this shouldn't save"

        doc = Document_.find(name="third")
        doc.text_ = "this is updated third test value"
        doc.save()
        assert Document_.find(name="third").text_ == "this is updated third test value"

    def test_document_update(self, populate_table):
        Document_ = self.__class__.Document_

        doc = Document_.find(name="first")
        doc.update(text_="this is updated first value")
        assert doc.text_ == "this is updated first value"
        assert Document_.find(name="first").text_ != "this is updated first value"

    def test_document_select(self, populate_table):
        Document_ = self.__class__.Document_

        rows = Document_.select(where="text_ like $text_like", vars={"text_like": "this is %"})
        assert len(rows) == 2

        rows = Document_.select(where="text_ like $text_like", vars={"text_like": "%first%"})
        assert len(rows) == 1

        rows = Document_.select(where={"name": "second"}, vars={})
        assert len(rows) == 1

        rows = Document_.select(where={"name": "third"}, vars={})
        assert len(rows) == 0

        rows = Document_.select(what="name", where=None, vars=None)
        names = [{**row} for row in rows]
        assert names == [{"name": "first"}, {"name": "second"}]
