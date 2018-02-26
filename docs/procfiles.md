# Procenv: Procfiles

Procfiles are a mechanism for declaring the commands of your application (e.g. web server, worker etc.).

## Declaring application commands

Application commands are declared are declared in separate lines in each Procfile. Each command declaration, and therefore Procfile line should have the following format

```yaml
{command_name}: {command}
```

In more details:

- `{command_name}` is the name of your command and it is an alphanumeric string (underscores are allowed too)
- `{command}` is the actual command used to launch the process process, such as `gunicorn -c gunicorn.py sl.wsgi:application`

## Example Procfile

```yaml
web: gunicorn -c gunicorn.py sl.wsgi:application
celery_worker: celery worker --app=sl.celery -l INFO
celery_beat: celery beat --app=sl.celery -l INFO
```
