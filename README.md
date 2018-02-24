# Procenv: Run, manage and monitor Procfile-based applications

Procenv is a command line program that:

1. Runs your application's processes based on a Procfile
2. Monitors your application's compliance with the environment (e.g. if it's binding to the port defined in the `PORT` environment variable) via checks
3. Reports it's status and findings via structured messages

## Installation

Procenv can be installed via PyPI (requires Python >= 3.6):

```
pipenv install procenv
```

## Usage

To run your application with Procenv, just run the `procenv` command in your terminal, after "`cd`ing" into your project's directory.

```
procenv
```

For configuration options and detailed documentation, head over to the [`docs`](docs/) directory.

## Motivation

Procenv started out of our need in [SourceLair](https://www.sourcelair.com) to help our customers diagnose common issues with their web applications (e.g. not binding on the right port or not knowing the connection details for their database). For that reason we needed a tool that would do couple of things

## How is Procenv different than...

- Heroku: ...
- Docker: ...
- Foreman or Honcho: ...

## License

Procenv is licensed under the [MIT License](LICENSE)

---

<center>
    Created for <a href="https://www.sourcelair.com">SourceLair</a> in SourceLair by SourceLair.
</center>
