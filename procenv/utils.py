from importlib import import_module
import functools
import os
import sys


@functools.lru_cache()
def detect_procfile():
    """
    Find the appropriate Procfile to run the application.
    """
    procfile = 'Procfile'
    env_var_procfile = os.getenv('PROCFILE')

    if env_var_procfile:
        if os.path.exists(env_var_procfile):
            procfile = env_var_procfile
        else:
            log(
                'PF10',
                f'Cannot find the Procfile "{env_var_procfile}" defined in '
                'the PROCFILE environment variable. Falling back to '
                f'"{procfile}"',
            )

    if not os.path.exists(procfile):
        return None

    return procfile


@functools.lru_cache()
def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by
    the last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        msg = f'{dotted_path} doesn\'t look like a module path'
        raise ImportError(msg) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        msg = (
            f'Module "{module_path}" does not define a "{class_name}"'
            'attribute/class'
        )
        raise ImportError(msg) from err


def log(code, message):
    """
    Log a Procenv message to stderr, with an optional message code.
    """
    message_prefix = '[Procenv Message]'
    code_prefix = f' ({code})' if code else ''
    prefix = f'{message_prefix}{code_prefix}'
    full_message = f'{prefix} {message}\n'
    sys.stderr.write(full_message)
