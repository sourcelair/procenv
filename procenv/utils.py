import sys


PROCENV_MESSAGE_PREFIX = '[Procenv Message]'


def log(message, message_code=None):
    """
    """
    code_prefix = f' ({message_code})' if message_code else ''
    prefix = f'{PROCENV_MESSAGE_PREFIX}{code_prefix}'
    full_message = f'{prefix} {message}\n'
    sys.stderr.write(full_message)
