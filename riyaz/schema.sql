
create table document (
    id integer primary key,
    parent_id integer references document,
    doctype text,
    key text,
    data JSON,

    UNIQUE (parent_id, doctype, key)
);

create index document_doctype_key_idx on document(doctype, key);
