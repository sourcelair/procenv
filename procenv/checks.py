import asyncio
import errno
import http.server
import os
import socketserver

from . import exceptions
from . import utils


class BaseCheck:
    """
    """
    interval = 5

    def preboot(self):
        """
        The preboot check runs before Procenv attempts to start the
        application.
        """
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
        while self.should_run:
            await asyncio.sleep(self.interval)
            self.check()


class ProcfileCheck(BaseCheck):
    def preboot(self):
        if not utils.detect_procfile():
            message = (
                'PF40',
                f'Cannot find a Procfile to run your application.',
            )
            return False, message

        return True


class DatabaseURLCheck(BaseCheck):
    def preboot(self):
        DATABASE_URL = os.getenv('DATABASE_URL')

        if DATABASE_URL:
            utils.log(
                'DB10',
                'Your application is expected to connect to its database at '
                f'"{DATABASE_URL}".',
            )

        return True


class RedisURLCheck(BaseCheck):
    def preboot(self):
        REDIS_URL = os.getenv('REDIS_URL')

        if REDIS_URL:
            utils.log(
                'RD10',
                'Your application is expected to connect to Redis '
                f'"{REDIS_URL}".',
            )

        return True


class PortBindCheck(BaseCheck):
    HTTP_HANDLER = http.server.SimpleHTTPRequestHandler
    PORT = int(os.getenv('PORT', 0))
    TCP_SERVER_ARGS = (('', PORT), HTTP_HANDLER)

    def _port_is_used(self):
        try:
            with socketserver.TCPServer(*self.TCP_SERVER_ARGS):
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
        The check should only run as long as  the `PORT` environment variable
        is available and the port defined in it is free to bind.
        """
        if not bool(self.PORT):
            return False

        return not self._port_is_used()

    def preboot(self):
        message = (
            f'Application is expected to bind to port {self.PORT}.'
        )
        utils.log('PB10', message)
        return True

    def check(self):
        if not self._port_is_used():
            message = f'Application is not binding to port {self.PORT}.'
            utils.log('PB40', message)


def load_check(dotted_path):
    """
    Return a Check instance, given a dotted path.
    """
    check_class = utils.import_string(dotted_path)

    if not issubclass(check_class, BaseCheck):
        msg = (
            f'Class "{check_class}" should be a subclass of "{BaseCheck}".'
        )
        raise exceptions.InvalidCheckException(msg)

    check = check_class()

    return check
