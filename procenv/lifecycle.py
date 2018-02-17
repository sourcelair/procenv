import asyncio
import sys

from . import utils


async def application():
    procfile = utils.detect_procfile()

    utils.log(
        f'Running application with Procfile "{procfile}".',
        'PE10'
    )
    args = ['honcho', '-f', procfile, 'start']
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    await process.wait()


def preboot(checks):
    at_least_one_check_has_failed = False

    for check in checks:
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

            utils.log(message, code)

    if at_least_one_check_has_failed:
        utils.log('Exiting because at least one preboot check failed', 'PE11')
        sys.exit(40)


def setup_checks(loop, checks):
    for check in checks:
        loop.create_task(check.main())


def start(checks):
    utils.log('PE00', '👋 Welcome to Procenv.')
    utils.log('PE01', 'Running pre-boot checks for your application.')
    preboot(checks)
    loop = asyncio.get_event_loop()
    application_task = loop.create_task(application())
    setup_checks(loop, checks)
    loop.run_until_complete(application_task)
