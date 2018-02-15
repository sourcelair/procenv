import asyncio
import errno
import http.server
import os
import socketserver
import sys

from . import utils


class StopCheckException(Exception):
    pass


class BaseCheck:
    """
    """
    interval = 5

    def setup(self):
        pass

    def check(self):
        raise NotImplemented('You have to implement the `check` method.')

    async def main(self):
        self.setup()

        try:
            while True:
                await asyncio.sleep(self.interval)
                self.check()
        except StopCheckException:
            return


class PortBindCheck(BaseCheck):
    """
    """

    HTTP_HANDLER = http.server.SimpleHTTPRequestHandler
    PORT = int(os.getenv('PORT'))
    TCP_SERVER_ARGS = (('', PORT), HTTP_HANDLER)

    def _port_is_used(self):
        try:
            with socketserver.TCPServer(*self.TCP_SERVER_ARGS) as httpd:
                return False
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                return True
            else:
                return False

        return False

    def setup(self):
        message = (
            f'👋 Hey. We expect your application to bind to port {self.PORT}.'
        )
        utils.log(message, 'PE10')

    def check(self):
        if self._port_is_used():
            raise StopCheckException()

        message = f'Application is not binding to port {self.PORT}.'
        utils.log(message, 'PE40')

