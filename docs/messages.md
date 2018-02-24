# Procenv: Messages

Procenv logs messages to `stderr` to let you know about the status of your application. Example:

```
[Procenv Message] (PE00) 👋 Welcome to Procenv
```

All Procenv messages have the following format `[Procenv Message] ({code}) {message}` and end with `\n` (UNIX-style new line).

The `{code}` of every Procenv message has the following format: `{component}{status}`. In this format:

- `{component}` is a 2-uppercase-latin-character code of the corresponding Procenv component (e.g. `PB` for the `PortBindCheck` component)
- `{status}` is a 2-digit number representing the status of the component in the following format:
    - `0X`: Message that should always appear (e.g. the welcome message)
    - `1X`: Informational message (e.g. the connection details of the database)
    - `2X`: Success message (e.g. application bound successfully to port)
    - `4X`: User error (e.g. applicaiton has not bound to port)
    - `5X`: Internal procenv error

Procenv status codes intentionally keep a resemblance to [HTTP status codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#1xx_Informational_responses) (e.g. 1xx is for informational responses, 2xx is for success responses etc.)

Below you can find documentation for all available Procenv messages.

## (PE) Procenv

...

### PE00: Welcome

...

```
[Procenv Message] (PE00) 👋 Welcome to Procenv
```

### PE01: Running preboot checks

...

```
[Procenv Message] (PE01) Running pre-boot checks for your application
```

### PE10: Running application with Procfile

...

```
[Procenv Message] (PE10) Running application with Procfile "{self.procfile}"
```

### PE11: Exiting because at least one preboot check failed

...

```
[Procenv Message] (PE11) Exiting because at least one preboot check failed
```

## (PF) Procfile

### PF10: Falling back to Procfile

...

```
[Procenv Message] (PF10) Cannot find the Procfile "{env_var_procfile}" defined in the PROCFILE environment variable. Falling back to "Procfile".
```

### PF40: Cannot find a Procfile to run your application

...

```
[Procenv Message] (PF40) ...
```

## (DB) Database Connection

### DB10: Database connection details

...

```
[Procenv Message] (DB10) Your application is expected to connect to its database at "{DATABASE_URL}"
```

## (RD) Redis Connection

### RD10: Redis connection details

...

```
[Procenv Message] (RD10) Your application is expected to connect to Redis at "{REDIS_URL}"
```

## (PB) Port Binding

### PB10: Announce port to bind

...

```
[Procenv Message] (PB10) Application is expected to bind to port "{PORT}"
```

### PB40: Application not bound to port

...

```
[Procenv Message] (PB40) Application has not bound to port "{PORT}"
```
