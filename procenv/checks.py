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

    def preboot(self):
        """
        The preboot check runs before Procenv attempts to start the
        application. If it does not return a True-ish value, Procenv will exit
        without attempting to run the application.
        """
        return True

    def setup(self):
        return True

    def check(self):
        return True

    @property
    def should_run(self):
        """
        All checks should run by default. Subclasses can re-implement this
        property in order to decide whether they should run or not.
        """
        return True

    async def main(self):
        if not self.should_run:
            return

        self.setup()

        try:
            while True:
                await asyncio.sleep(self.interval)
                self.check()
        except StopCheckException:
            return


class ProcfileCheck(BaseCheck):
    """
    """
    def preboot(self):
        if not utils.detect_procfile():
            message = (
                f'Cannot find a Procfile to run your application.',
                'PF40'
            )
            return False, message

        return True


class DatabaseURLCheck(BaseCheck):
    """
    """
    def preboot(self):
        DATABASE_URL = os.getenv('DATABASE_URL')

        if DATABASE_URL:
            utils.log(
                'Your application is expected to connect to its database at '
                f'"{DATABASE_URL}".',
                'DB10'
            )

        return True


class RedisURLCheck(BaseCheck):
    """
    """
    def preboot(self):
        REDIS_URL = os.getenv('REDIS_URL')

        if REDIS_URL:
            utils.log(
                'Your application is expected to connect to Redis '
                f'"{REDIS_URL}".',
                'RD10'
            )

        return True


class PortBindCheck(BaseCheck):
    """
    """

    HTTP_HANDLER = http.server.SimpleHTTPRequestHandler
    PORT = int(os.getenv('PORT', 0))
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

    @property
    def should_run(self):
        """
        The check should only run if the `PORT` environment variable is
        available.
        """
        return bool(self.PORT)

    def preboot(self):
        message = (
            f'Application is expected to bind to port {self.PORT}.'
        )
        utils.log(message, 'PB10')
        return True

    def check(self):
        if self._port_is_used():
            raise StopCheckException()

        message = f'Application is not binding to port {self.PORT}.'
        utils.log(message, 'PB40')
