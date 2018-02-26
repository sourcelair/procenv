import click

from . import utils
from .applications import ProcfileApplication
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
    help='Checks to use when running the Procfile-based application'
)
def main(check):
    """
    Procenv lets you run, manage and monitor Procfile-based applications.
    """
    utils.log('PE00', '👋 Welcome to Procenv')
    checks = [load_check(path) for path in check]
    app = ProcfileApplication(
        procfile=utils.detect_procfile(),
        checks=checks,
    )
    app.run_preboot_checks()
    app.setup_main_checks()
    app.run_and_wait_for_application()


if __name__ == '__main__':
    main()
