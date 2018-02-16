import asyncio
import sys

from . import checks
from . import utils


async def boot():
    utils.log(
        '👋 Procenv booted. Preparing to run your application.',
        'PE00'
    )
    procfile = utils.detect_procfile()

    if not procfile:
        utils.log(
            f'Cannot find a Procfile to run your application.',
            'PE40'
        )
        return

    utils.log(
        f'Using "{procfile}" to run your application.',
        'PE02'
    )
    args = ['honcho', '-f', procfile, 'start']
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    code = await process.wait()


def main():
    loop = asyncio.get_event_loop()
    boot_task = loop.create_task(boot())
    check_port_task = loop.create_task(checks.PortBindCheck().main())
    loop.run_until_complete(boot_task)

if __name__ == '__main__':
    main()
