import asyncio
import sys

from . import checks
from . import utils


async def application():
    utils.log(
        '👋 Procenv booted. Preparing to run your application.',
        'PE00'
    )
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
    code = await process.wait()


def main():
    procfile_check = checks.ProcfileCheck()
    port_bind_check = checks.PortBindCheck()
    _checks = [procfile_check, port_bind_check]

    for check in _checks:
        if not check.preboot():
            utils.log(
                f'Check {check.__class__.__name__}.preboot() failed.',
                code='PE40'
            )
            sys.exit(40)

    loop = asyncio.get_event_loop()
    boot_task = loop.create_task(application())

    for check in _checks:
        check_port_task = loop.create_task(check.main())

    loop.run_until_complete(boot_task)

if __name__ == '__main__':
    main()
