import asyncio
import errno
import http.server
import os
import socketserver

from . import exceptions
from . import utils


class BaseCheck:
    """
    Base class for implementing checks. To run a check in the `preboot` stage,
    then implement the `preboot` method. To run a check in the `main` stage,
    then implement the `main` and the `should_main_check_run` method.
    """
    interval = 5

    async def main_loop(self):
        if not hasattr(self, 'should_main_check_run'):
            msg = (
                f'Check "{self}" should implement the '
                '"should_main_check_run" method, in order to run its "main" '
                'check'
            )
            raise NotImplementedError(msg)

        while self.should_main_check_run():
            await asyncio.sleep(self.interval)
            self.main()


class ProcfileCheck(BaseCheck):
    def preboot(self):
        if not utils.detect_procfile():
            message = (
                'PF40',
                f'Cannot find a Procfile to run your application',
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
                f'"{DATABASE_URL}"',
            )

        return True


class RedisURLCheck(BaseCheck):
    def preboot(self):
        REDIS_URL = os.getenv('REDIS_URL')

        if REDIS_URL:
            utils.log(
                'RD10',
                'Your application is expected to connect to Redis at '
                f'"{REDIS_URL}"',
            )

        return True


class PortBindCheck(BaseCheck):
    """
    The Port Bind Check monitors if the port requested is available for
    binding.
    """

    def __init__(self, port=None):
        self.port = port or int(os.getenv('PORT', 0))

    def get_tcp_server_for_port(self):
        """
        Create a TCP server binding to the port of the check. This is used to
        find out the availability of this port.
        """
        server = socketserver.TCPServer(
            ('', self.port), http.server.SimpleHTTPRequestHandler,
        )

        return server

    def port_is_being_used(self):
        try:
            with self.get_tcp_server_for_port():
                return False
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                return True
            raise e

        return False

    def should_main_check_run(self):
        """
        The check should only run as long as  the `PORT` environment variable
        is available and the port defined in it is free to bind.
        """
        if not bool(self.port):
            return False

        return not self.port_is_being_used()

    def preboot(self):
        message = (
            f'Application is expected to bind to port "{self.port}"'
        )
        utils.log('PB10', message)
        return True

    def main(self):
        if not self.port_is_being_used():
            message = f'Application has not bound to port "{self.port}"'
            utils.log('PB40', message)
        else:
            message = f'Application bound successfully to port "{self.port}"'
            utils.log('PB20', message)


def load_check(dotted_path):
    """
    Return a Check instance, given a dotted path.
    """
    check_class = utils.import_string(dotted_path)

    if not issubclass(check_class, BaseCheck):
        msg = (
            f'Class "{check_class}" should be a subclass of "{BaseCheck}"'
        )
        raise exceptions.InvalidCheckException(msg)

    check = check_class()

    return check
