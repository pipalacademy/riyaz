
create table course (
    id integer primary key,
    key text unique,
    title text not null,
    short_description text,
    description text
);

create table instructor (
    id integer primary key,
    key text unique,
    name text not null,
    about text,
    photo_path text
);

create table course_instructor (
    id integer primary key,
    course_id integer references course,
    instructor_id integer references instructor,
    index_ integer,
    unique(course_id, instructor_id)
);

create table module (
    id integer primary key,
    course_id integer references course,
    name text,
    title text,
    index_ integer,

    unique (course_id, name)
);

create table lesson (
    id integer primary key,
    course_id integer references course,
    module_id integer references module,
    index_ integer,
    name text,
    title text,
    content text,

    unique (course_id, module_id, name)
);

create table course_outline (
    id integer primary key,
    course_id integer references course,

    module_id integer references module,
    module_index integer,

    lesson_id integer references lesson,
    lesson_index integer,

    prev_lesson_id integer references lesson,
    prev_lesson_index integer,

    next_lesson_id integer references lesson,
    next_lesson_index integer,

    orphan boolean default('f')
);

create table store (
    id integer primary key,
    key text unique,
    value text
);

create table asset (
    id integer primary key,

    collection text,
    collection_id int,
    filename text,

    filesize int,
    created datetime,
    last_modified datetime
);

-- create view course_outline_view as
-- select
--     course_outline.*,
--     module.name as module_name, module.title as module_title, format("%d", module_index) as module_label,
--     lesson.name as lesson_name, lesson.title as lesson_title, format("%d.%d", module_index, lesson_index),
--     next_lesson.name as next_lesson_name, next_lesson.title as next_lesson_title,
--     prev_lesson.name as prev_lesson_name, prev_lesson.title as prev_lesson_title
-- from course_outline
-- JOIN module on module.id=course_outline.module_id
-- JOIN lesson on lesson.id=course_outline.lesson_id
-- JOIN lesson as next_lesson on next_lesson.id=course_outline.next_lesson_id
-- JOIN lesson as prev_lesson on prev_lesson.id=course_outline.prev_lesson_id;
