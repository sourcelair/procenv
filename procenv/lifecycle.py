import asyncio
import sys

from . import utils


async def application():
    procfile = utils.detect_procfile()

    utils.log(
        'PE10',
        f'Running application with Procfile "{procfile}".',
    )
    args = ['honcho', '-f', procfile, 'start']
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    await process.wait()


def run_preboot_checks(checks):
    at_least_one_check_has_failed = False
    preboot_checks = [check for check in checks if hasattr(check, 'preboot')]

    for check in preboot_checks:
        preboot_result = check.preboot()

        if (type(preboot_result) == tuple):
            succeedded, reason = preboot_result
        else:
            succeedded = preboot_result
            reason = None

        if not succeedded:
            at_least_one_check_has_failed = True

            if reason:
                message, code = reason
                message = (
                    f'Check {check.__class__.__name__}.preboot() failed: '
                    f'{message}'
                )
            else:
                message = reason
                code = 'PE40'

            utils.log(code, message)

    if at_least_one_check_has_failed:
        utils.log('PE11', 'Exiting because at least one preboot check failed')
        sys.exit(40)


def setup_main_checks(loop, checks):
    main_checks = [check for check in checks if hasattr(check, 'main')]

    for check in main_checks:
        loop.create_task(check.main_loop())


def start(checks):
    utils.log('PE00', '👋 Welcome to Procenv.')
    utils.log('PE01', 'Running pre-boot checks for your application.')
    run_preboot_checks(checks)
    loop = asyncio.get_event_loop()
    application_task = loop.create_task(application())
    setup_main_checks(loop, checks)
    loop.run_until_complete(application_task)
