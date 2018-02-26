# Procenv: Run, manage and monitor Procfile-based applications

[![Build Status](https://travis-ci.org/sourcelair/procenv.svg?branch=master)](https://travis-ci.org/sourcelair/procenv)

Procenv is a command line program that:

1. Runs a Procfile-based application
2. Monitors the application's compliance with the environment via given checks (e.g. does it bind to the port defined in the `PORT` environment variable?)
3. Reports the application's status and findings via structured messages to stderr

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

Procenv started out of our need in [SourceLair](https://www.sourcelair.com) to help our customers diagnose common issues with their web applications (e.g. not binding on the right port or not knowing the connection details for their database). For that reason we needed a tool that would carry out 2 tasks concurrently:

1. Run Procfile-based applications
2. Check and report the status of these applications

## How is Procenv different than...

### Heroku
Heroku is a complete platform for running Procfile-based applications. It provides features as scaling your application, deploy your application via Git etc. Procenv runs the application "locally" and reports it's status to stderr.

### Docker or Docker Compose
Docker and Docker Compose take care of isolating, packaging and running whole stacks. Procenv focuses on running the main processes of your application based on a `Procfile`, which is quite simpler than a `docker-compose.yml` file. Procenv will not take care of running your database or Redis server, as Docker and Docker Compose can.

## Foreman or Honcho
Procenv is a superset of these tools. Actually, Procenv relies on Honcho to run Procfile-based applications.

## License

Procenv is licensed under the [MIT License](LICENSE)

---

<center>
    Created for <a href="https://www.sourcelair.com">SourceLair</a> in SourceLair by SourceLair.
</center>
