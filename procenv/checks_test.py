from unittest import mock
import asyncio
import errno
import http.server
import unittest

from . import checks
from . import exceptions


class BaseCheckTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def test_main_loop(self):
        """
        Ensure that running the `main_loop` on a legit subclass of BaseCheck,
        then the `main` method is being called, until `should_main_check_run`
        returns False
        """
        # The `sync_asyncio_sleep` function will help us capture the call to
        # the `asyncio.sleep` coroutine function.
        sync_asyncio_sleep_mock = mock.MagicMock()

        async def asyncio_sleep_mock(*args, **kwargs):
            # Proxy the call to `sync_mock_process_wait`, to capture it.
            sync_asyncio_sleep_mock(*args, **kwargs)
            return True

        class LegitCheck(checks.BaseCheck):
            interval = 100
            main = mock.MagicMock()
            _times_run = 0

            def should_main_check_run(self):
                """
                The `main` should run two times in total.
                """
                self._times_run += 1

                if self._times_run > 2:
                    return False

                return True

        legit_check = LegitCheck()

        with mock.patch('asyncio.sleep', new=asyncio_sleep_mock):
            self.loop.run_until_complete(legit_check.main_loop())

        expected_asyncio_sleep_call_args_list = [
            mock.call(LegitCheck.interval), mock.call(LegitCheck.interval),
        ]
        assert sync_asyncio_sleep_mock.call_args_list == expected_asyncio_sleep_call_args_list  # noqa

        expected_main_call_args_list = [mock.call(), mock.call()]
        assert legit_check.main.call_args_list == expected_main_call_args_list

    def test_main_loop_no_should_main_check_run(self):
        """
        Ensure that when a subclass of `BaseCheck` does not implement the
        `should_main_check_run` method, the appropriate exception gets raised.
        """
        class ScumCheck(checks.BaseCheck):
            # No implementation of `should_main_check_run`
            pass

        scum_check = ScumCheck()
        try:
            self.loop.run_until_complete(scum_check.main_loop())
        except NotImplementedError as e:
            expected_message = (
                f'Check "{scum_check}" should implement the '
                '"should_main_check_run" method, in order to run its "main" '
                'check'
            )
            assert str(e) == expected_message


def test_procfile_preboot_check():
    check = checks.ProcfileCheck()

    # Assert that when a Procfile is found, then `True` is being returned.
    with mock.patch(
        'procenv.utils.detect_procfile',
        return_value='Procfile.test',
    ) as detect_procfile_stub:
        assert check.preboot() is True
        detect_procfile_stub.assert_called_once_with()

    # Assert that when a Procfile is not found, then `False`, along with an
    # error message are being returned.
    with mock.patch('procenv.utils.detect_procfile', return_value=None):
        error_message = (
            'PF40',
            f'Cannot find a Procfile to run your application',
        )
        assert check.preboot() == (False, error_message)


def test_database_url_preboot_check():
    check = checks.DatabaseURLCheck()

    # Assert that when the DATABASE_URL environment variable is available,
    # then the preboot check will log the appropriate informative message.
    with mock.patch('os.getenv', return_value='ledatabaseurl'):
        with mock.patch('procenv.utils.log') as log_stub:
            assert check.preboot() is True
            log_stub.assert_called_once_with(
                'DB10',
                'Your application is expected to connect to its database at '
                '"ledatabaseurl"',
            )

    # Assert that when the DATABASE_URL environment variable is not available,
    # then the preboot check will log nothing.
    with mock.patch('os.getenv', return_value=None):
        with mock.patch('procenv.utils.log') as log_stub:
            assert check.preboot() is True
            assert log_stub.called is False


def test_redis_url_preboot_check():
    check = checks.RedisURLCheck()

    # Assert that when the REDIS_URL environment variable is available,
    # then the preboot check will log the appropriate informative message.
    with mock.patch('os.getenv', return_value='leredis'):
        with mock.patch('procenv.utils.log') as log_stub:
            assert check.preboot() is True
            log_stub.assert_called_once_with(
                'RD10',
                'Your application is expected to connect to Redis at '
                '"leredis"',
            )

    # Assert that when the REDIS_URL environment variable is not available,
    # then the preboot check will log nothing.
    with mock.patch('os.getenv', return_value=None):
        with mock.patch('procenv.utils.log') as log_stub:
            assert check.preboot() is True
            assert log_stub.called is False


class PortBindCheckTest(unittest.TestCase):
    def test_init(self):
        """
        Ensure that the PortBindCheck constructor sets the appropriate value
        to the port attribute of its instances.
        """
        with mock.patch('os.getenv', return_value='4000'):
            check_with_no_port_provided = checks.PortBindCheck()
            assert check_with_no_port_provided.port == 4000

            check_with_port_provided = checks.PortBindCheck(port=5000)
            assert check_with_port_provided.port == 5000

    def test_get_tcp_server_for_port(self):
        """
        Ensure that the `get_tcp_server_for_port`, makes the appropriate call
        to `socketserver.TCPServer` and returns the return value.
        """
        port = 8000
        check = checks.PortBindCheck(port=port)
        tcp_server_instance_mock = mock.MagicMock()

        with mock.patch(
            'socketserver.TCPServer',
            return_value=tcp_server_instance_mock,
        ) as tcp_server_mock:
            assert check.get_tcp_server_for_port() == tcp_server_instance_mock
            tcp_server_mock.assert_called_once_with(
                ('', port), http.server.SimpleHTTPRequestHandler,
            )

    def test_port_is_being_used(self):
        """
        Ensure that the `port_is_being_used` method returns `False` if the
        port attribute of the check is available to bind.
        """
        port = 8000
        check = checks.PortBindCheck(port=port)

        # Integration test: Make sure that if no process has bound to the
        # above port, then `port_is_being_used` returns False.
        assert check.port_is_being_used() is False

        # Integration test: Make sure that if a process has bound to the
        # above port, then `port_is_being_used` returns True.
        with check.get_tcp_server_for_port():
            assert check.port_is_being_used() is True

        # Ensure that `port_is_being_used` makes the appropriate call to
        # `get_tcp_server_for_port` and that if an `OSError` exception with
        # errno EADDRINUSE gets raised with the appropriate errno, then it is
        # being handled gracefully.
        with mock.patch(
            'procenv.checks.PortBindCheck.get_tcp_server_for_port',
            side_effect=OSError(errno.EADDRINUSE, 'Address already in use'),
        ) as get_tcp_server_for_port_mock:
            assert check.port_is_being_used() is True
            get_tcp_server_for_port_mock.assert_called_once()

        # Ensure that other exceptions get reraised.
        weird_exception = OSError(errno.EINTR, 'Interrupted system call')

        try:
            with mock.patch(
                'procenv.checks.PortBindCheck.get_tcp_server_for_port',
                side_effect=weird_exception,
            ) as get_tcp_server_for_port_mock:
                check.port_is_being_used()
        except Exception as e:
            assert e == weird_exception

    def test_should_main_check_run(self):
        """
        Ensure that the `should_main_check_run` method returns False, if no
        `port` is defined, or else it returns the boolean negative of
        `port_is_being_used`.
        """
        check = checks.PortBindCheck()
        check.port = None

        assert check.should_main_check_run() is False

        check.port = 11235

        with mock.patch(
            'procenv.checks.PortBindCheck.port_is_being_used',
            return_value=True,
        ):
            assert check.should_main_check_run() is False

        with mock.patch(
            'procenv.checks.PortBindCheck.port_is_being_used',
            return_value=False,
        ):
            assert check.should_main_check_run() is True

    def test_preboot(self):
        """
        Make sure that the `preboot` check always logs an informative message
        about the port that the application is expected to bind to.
        """
        check = checks.PortBindCheck(12345)

        with mock.patch('procenv.utils.log') as log_mock:
            check.preboot()

        log_mock.assert_called_once_with(
            'PB10',
            'Application is expected to bind to port "12345"',
        )

    def test_main(self):
        """
        Make sure that the `main` check always logs an informative message
        about the port that the application is expected to bind to.
        """
        check = checks.PortBindCheck(31415)

        with mock.patch('procenv.utils.log') as log_mock:
            with mock.patch(
                'procenv.checks.PortBindCheck.port_is_being_used',
                return_value=False,
            ):
                check.main()
                log_mock.assert_called_once_with(
                    'PB40',
                    'Application has not bound to port "31415"',
                )

        with mock.patch('procenv.utils.log') as log_mock:
            with mock.patch(
                'procenv.checks.PortBindCheck.port_is_being_used',
                return_value=True,
            ):
                check.main()
                log_mock.assert_called_once_with(
                    'PB20',
                    'Application bound successfully to port "31415"',
                )


def test_load_check():
    """
    Make sure that `load_check` returns an instance of the appropriate check,
    or raises the appropriate error.
    """
    # Assert that attempting to load a legit check, will make the appropriate
    # call to `utils.import_string` and return an instance of the returned
    # class, if it is a subclass of BaseCheck.
    with mock.patch(
        'procenv.utils.import_string',
        return_value=checks.PortBindCheck,
    ) as import_string_stub:
        check_dotted_path = 'procenv.checks.PortBindCheck'
        check = checks.load_check(check_dotted_path)
        import_string_stub.assert_called_once_with(check_dotted_path)
        assert isinstance(check, checks.PortBindCheck)

    # Assert that attempting to load a legit check, will raise the appropriate
    # exception if the dotted path does not resolve to a `BaseCheck` subclass.
    class ScumCheck:
        """
        This is not a subclass of `checks.BaseCheck` apparently.
        """

    with mock.patch(
        'procenv.utils.import_string',
        return_value=ScumCheck,
    ) as import_string_stub:
        check_dotted_path = 'procenv.checks.PortBindCheck'

        try:
            check = checks.load_check(check_dotted_path)
        except exceptions.InvalidCheckException as e:
            expected_exception_message = (
                f'Class "{ScumCheck}" should be a subclass of '
                f'"{checks.BaseCheck}"'
            )
            assert str(e) == expected_exception_message
