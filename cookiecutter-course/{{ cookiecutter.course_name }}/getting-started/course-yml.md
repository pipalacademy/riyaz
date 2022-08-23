# course.yml

`course.yml` is where the course metadata and ordering of lessons and modules goes. 

```yaml
name: sample-course
title: Sample Course

short_description: A sample course
description: |
    This is a sample course.

    This section supports markdown.
    Text can be **bold**, *italicized*, __underlined__, or as `code`.

authors:
    - alice

outline:
    - name: getting-started
      title: Getting Started
      lessons:
        - getting-started/riyaz-terminology.md
        - getting-started/course-yml.md
```

The `name` is the unique key for that course, and it appears in the URL path.
The `title` is the course title that will be rendered on the HTML page.

Each author is expected to have a markdown file about them at
`course-base/authors/{author-key}.md`. `{author-key}` is the key that is used
in `course.yml` to refer to that file (here, alice).
`alice.md` will then have the author's full name (`name`) and photo (`photo`)
in YAML frontmatter, and the about section as its content.

Outline is a list of modules for the course. Each module will have a `name`
(that will show in URL path) and a `title` (that will be rendered in HTML).
It will have a list of paths to lesson files.
Here there is one module (`getting-started`) and it has two lessons.
