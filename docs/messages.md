# Procenv: Messages

Procenv logs messages to `stderr` to let you know about the status of your application. Example:

```
[Procenv Message] (PE00) 👋 Welcome to Procenv
```

All Procenv messages have the following format `[Procenv Message] ({code}) {message}` and end with `\n` (UNIX-style new line).

The `{code}` of every Procenv message has the following format: `{component}{status}`. In this format:

- `{component}` is a 2-uppercase-latin-character code of the corresponding Procenv component:
    - `PE`: Procenv
    - `PF`: ProcfileCheck
    - `DB`: DatabaseURLCheck
    - `RD`: RedisURLCheck
    - `PB`: PortBindCheck
- `{status}` is a 2-digit number representing the status of the component in the following format:
    - `0X`: Message that should always appear (e.g. the welcome message)
    - `1X`: Informational message (e.g. the connection details of the database)
    - `2X`: Success message (e.g. application bound successfully to port)
    - `4X`: User error (e.g. applicaiton has not bound to port)
    - `5X`: Internal procenv error

Procenv status codes intentionally keep a resemblance to [HTTP status codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#1xx_Informational_responses) (e.g. 1xx is for informational responses, 2xx is for success responses etc.) and [Heroku Error Codes](https://devcenter.heroku.com/articles/error-codes) (component code, error code) at the same time.

Below you can find documentation for all available Procenv messages.

## PE00 - Welcome

Welcome message when Procenv loads -- this should be the first message to be printed when Procenv loads.

```
[Procenv Message] (PE00) 👋 Welcome to Procenv
```

## PE01 - Preboot checks running

Printed when the preboot checks of the applications start to run.

```
[Procenv Message] (PE01) Running preboot checks for your application
```

## PE10 - Running application with Procfile

Printed when the Procfile to run the application is being detected successfully.

```
[Procenv Message] (PE10) Running application with Procfile "{self.procfile}"
```

## PE11 - Exiting because at least one preboot check failed

At least one preboot check failed, so the application cannot run and Procenv exits.

```
[Procenv Message] (PE11) Exiting because at least one preboot check failed
```

## PF10 - Falling back to Procfile

ProcfileCheck could not find the Procfile defined in the `PROCFILE` environment variable and falls back to the default Procfile name; `Procfile`.

```
[Procenv Message] (PF10) Cannot find the Procfile "{env_var_procfile}" defined in the PROCFILE environment variable. Falling back to "Procfile".
```

## PF40 - Cannot find a Procfile to run your application

ProcfileCheck could not locate a valid Procfile to run the application.

```
[Procenv Message] (PF40) Cannot find a Procfile to run your application
```

## DB10 - Database connection details

Procenv detected a `DATABASE_URL` environment variable, so it prints a message to let the user know where is the application expected to find its database.

```
[Procenv Message] (DB10) Your application is expected to connect to its database at "{DATABASE_URL}"
```

## RD10 - Redis connection details

Procenv detected a `REDIS_URL` environment variable, so it prints a message to let the user know where is the application expected to find Redis.

```
[Procenv Message] (RD10) Your application is expected to connect to Redis at "{REDIS_URL}"
```

## PB10 - Port to bind

Procenv detected lets the user know to which port is the application expected to bind, according to the `PORT` environment variable.

```
[Procenv Message] (PB10) Application is expected to bind to port "{PORT}"
```

## PB20 - Application bound to port successfully

Application successfully bound to the port declared in the `PORT` environment variable.

```
[Procenv Message] (PB20) Application bound successfully to port "{PORT}"
```

## PB40 - Application not bound to port

The port declared in the `PORT` environment variable is available, so it's assumed that the application has not bound to it yet.

```
[Procenv Message] (PB40) Application has not bound to port "{PORT}"
```
