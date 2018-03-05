# Procenv: Checks

Procenv monitors the status and health of Procfile based applications by using **Checks**.

Each Check can run either in the `preboot` stage of the application, or lopp during the `main` loop or both.

## ProcfileCheck

Checks if the Procfile defined in the `PROCFILE` environment variable exists. If the `PROCFILE` is not set, or its value does not exist in the file system, the `ProcfileCheck` will fall back to the default value (`Procfile`) and check again if the file exists.

This check runs during the `preboot` stage of the application.

If no Procfile can be found, then the check fails, returns `False` and Procenv will exit.

## DatabaseURLCheck

Just checks if the `DATABASE_URL` environment variable is set and if it is, it prints a log message iforming the user about the connection details of the application's database. If no `DATABASE_URL` environment variable is set, nothing happens.

This check runs during the `preboot` stage of the application.

## RedisURLCheck

Just checks if the `REDIS_URL` environment variable is set and if it is, it prints a log message iforming the user about the connection details of Redis. If no `REDIS_URL` environment variable is set, nothing happens.

This check runs during the `preboot` stage of the application.

## PortBindCheck

Checks if the application binds successfully to the port defined in the `PORT` environment variable.

This check runs in both stages:

- `preboot`: Prints an informational log message, letting the user know to which port should the application bind
- `main`: Prints an error message, if the application has not bound to the corresponding port (repeats every 5 seconds)
