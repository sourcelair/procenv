# Procenv: Command Line Interface

Procenv can be used via its Command Line Interface in a terminal.

## Usage

```
$ procenv --help
Usage: procenv [OPTIONS]

  Procenv lets you run, manage and monitor Procfile-based applications.

Options:
  -c, --check TEXT  Checks to use when running the Procfile-based application
                    [default: procenv.checks.ProcfileCheck,
                    procenv.checks.PortBindCheck,
                    procenv.checks.DatabaseURLCheck,
                    procenv.checks.RedisURLCheck]
  --help            Show this message and exit.
```

## Options

### check

The `--check` (or `-c`) command line argument is being used to determine which Procenv checks should run for the application.

Each check should be defined as a Python dotted path to the corresponding check class. This means that you can also define and run your own custom checks too 🙌!

Multiple checks can be defined and run, by passing the `--check` argument multiple times:

```
procenv --check procenv.checks.ProcfileCheck --check procenv.checks.PortBindCheck
```

## Example

```
$ procenv
[Procenv Message] (PE00) 👋 Welcome to Procenv
[Procenv Message] (PE01) Running preboot checks for your application
[Procenv Message] (PB10) Application is expected to bind to port "8000"
[Procenv Message] (PE10) Running application with Procfile "Procfile.legit"
13:04:24 system | web.1 started (pid=39)
13:04:25 web.1  | Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
[Procenv Message] (PB20) Application bound successfully to port "8000"
```
