import click

from . import lifecycle
from . import utils


DEFAULT_CHECKS = [
    'procenv.checks.ProcfileCheck',
    'procenv.checks.PortBindCheck',
    'procenv.checks.DatabaseURLCheck',
    'procenv.checks.RedisURLCheck',
]
DEFAULT_CHECKS_ARG = ','.join(DEFAULT_CHECKS)


@click.command()
@click.option(
    '--checks',
    default=DEFAULT_CHECKS_ARG,
    help='Checks to use when running the Procfile-based application.'
)
def run(checks):
    """
    Run Procenv with the given checks.
    """
    actual_checks = [
        utils.import_string(check)() for check in checks.split(',')
    ]
    lifecycle.start(checks=actual_checks)


if __name__ == '__main__':
    run()
