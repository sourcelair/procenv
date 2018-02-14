import asyncio
import errno
import http.server
import os
import socketserver
import sys


def port_is_used():
    port = int(os.getenv('PORT'))
    handler = http.server.SimpleHTTPRequestHandler

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            return False
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            return True
        else:
            raise e

    return False


async def honcho():
    # Run an echo subprocess
    process = await asyncio.create_subprocess_exec(
        'honcho', 'start',
        # stdout must a pipe to be accessible as process.stdout
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    code = await process.wait()


async def periodic():
    while True:
        p = port_is_used()
        print(f'port is used: {p}')
        await asyncio.sleep(5)

def stop():
    task.cancel()

task = asyncio.Task(periodic())
loop = asyncio.get_event_loop()

asyncio.async(periodic())
loop.run_until_complete(honcho())
loop.close()
