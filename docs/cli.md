# Riyaz CLI

## Installation

```shell
$ pip install riyaz
```

## Usage

Create a new project template with `riyaz new <project-dir>`

```shell
$ riyaz new alpha-course
```

This will create a project structure like:

```
alpha-course/
|-- course.yml
|-- authors/
|-- |-- alice.md
|-- module-1/
|-- |-- getting-started.md
|-- module-2/
|__ |__ more-advanced-things.md
```

You can see the course in action with:

```shell
$ riyaz serve
```

You can rename the modules and lessons, add/edit content, change the configuration in `course.yml`
to use the new content. Then again when you want to check how the content wil appear on Riyaz,
you can run `riyaz serve` and make final touchups.

When you are ready to push it to the central repository (or another remote), you can run
`riyaz push`.

```shell
$ riyaz push
```

*TODO: Add a way to login*
