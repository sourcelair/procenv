import click

from . import lifecycle
from .checks import load_check


DEFAULT_CHECKS = [
    'procenv.checks.ProcfileCheck',
    'procenv.checks.PortBindCheck',
    'procenv.checks.DatabaseURLCheck',
    'procenv.checks.RedisURLCheck',
]


@click.command()
@click.option(
    '-c',
    '--check',
    default=DEFAULT_CHECKS,
    multiple=True,
    show_default=True,
    help='Checks to use when running the Procfile-based application.'
)
def run(check):
    """
    Procenv lets you run, monitor and manage Procfile-based applications.
    """
    checks = [load_check(path) for path in check]
    lifecycle.start(checks=checks)


if __name__ == '__main__':
    run()
