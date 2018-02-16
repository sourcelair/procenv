import asyncio
import sys

from . import checks
from . import utils


async def honcho():
    # Run an echo subprocess
    process = await asyncio.create_subprocess_exec(
        'honcho', 'start',
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    code = await process.wait()


def main():
    loop = asyncio.get_event_loop()
    check_port_task = loop.create_task(checks.PortBindCheck().main())
    loop.run_until_complete(honcho())

if __name__ == '__main__':
    main()
