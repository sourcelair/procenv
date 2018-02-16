import os
import sys


PROCENV_MESSAGE_PREFIX = '[Procenv Message]'


def log(message, code=None):
    """
    Log a Procenv message to stderr, with an optional message code.
    """
    code_prefix = f' ({code})' if code else ''
    prefix = f'{PROCENV_MESSAGE_PREFIX}{code_prefix}'
    full_message = f'{prefix} {message}\n'
    sys.stderr.write(full_message)


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
                f'Cannot find the Procfile "{env_var_procfile}" defined in '
                'the PROCFILE environment variable. Falling back to '
                f'"{procfile}".',
                'PE01'
            )

    if not os.path.exists(procfile):
        return None

    return procfile
