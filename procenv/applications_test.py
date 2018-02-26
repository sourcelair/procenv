from unittest import mock
import asyncio
import sys
import unittest

from . import applications
from . import checks


class DummyPrebootCheck(checks.BaseCheck):
    def preboot(self):
        return True


class DummyMainCheck(checks.BaseCheck):
    def main(self):
        return True


class DummyPrebootAndMainCheck(checks.BaseCheck):
    def preboot(self):
        return True

    def main(self):
        return True


class ProcfileApplicationTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.procfile = 'Procfile.hey'
        self.dummy_preboot_check = DummyPrebootCheck()
        self.dummy_main_check = DummyMainCheck()
        self.dummy_preboot_and_main_check = DummyPrebootAndMainCheck()
        self.all_checks = [
            self.dummy_preboot_check,
            self.dummy_main_check,
            self.dummy_preboot_and_main_check,
        ]
        self.app = applications.ProcfileApplication(
            procfile=self.procfile, checks=self.all_checks, loop=self.loop,
        )

    def test_init(self):
        """
        Ensure that creating a new `ProcfileApplication` instance, assigns
        the appropriate attributes.
        """
        # ProcfileApplication without explicit event loop
        loop_mock = mock.MagicMock()
        with mock.patch(
            'asyncio.get_event_loop',
            return_value=loop_mock,
        ):
            app_without_loop = applications.ProcfileApplication(
                procfile=self.procfile, checks=self.all_checks,
            )
            assert app_without_loop.procfile == self.procfile
            assert app_without_loop.checks == self.all_checks
            assert app_without_loop.loop == loop_mock

        # ProcfileApplication with an explicit event loop
        loop = asyncio.get_event_loop()
        app_with_loop = applications.ProcfileApplication(
            procfile=self.procfile,
            checks=self.all_checks,
            loop=loop,
        )
        assert app_with_loop.procfile == self.procfile
        assert app_with_loop.checks == self.all_checks
        assert app_with_loop.loop == loop

    def test_cmd(self):
        """
        Ensure that the `cmd` property returns the appropriate command to run
        to execute the application subprocess.
        """
        assert self.app.cmd == ['honcho', '-f', self.procfile, 'start']

    def test_preboot_checks(self):
        """
        Ensure that the `preboot_checks` property returns only the checks that
        implement the `preboot` method.
        """
        preboot_checks = [
            self.dummy_preboot_check, self.dummy_preboot_and_main_check,
        ]
        assert self.app.preboot_checks == preboot_checks

    def test_main_checks(self):
        """
        Ensure that the `main_checks` property returns only the checks that
        implement the `main` method.
        """
        main_checks = [
            self.dummy_main_check, self.dummy_preboot_and_main_check,
        ]
        assert self.app.main_checks == main_checks

    def test_run_preboot_checks(self):
        """
        Ensure that the `run_preboot_checks` method prints the appropriate
        messages and runs the expected checks and that the process is NOT
        exiting afterwards.
        """
        succeeding_preboot_check_a = mock.MagicMock()
        succeeding_preboot_check_a.preboot.return_value = True
        succeeding_preboot_check_b = mock.MagicMock()
        succeeding_preboot_check_b.preboot.return_value = True

        app = applications.ProcfileApplication(
            procfile=self.procfile,
            checks=[succeeding_preboot_check_a, succeeding_preboot_check_b],
        )

        with mock.patch('sys.exit') as exit_mock:
            with mock.patch('procenv.utils.log') as log_mock:
                app.run_preboot_checks()

        expected_log_mock_call_args_list = [
            mock.call(
                'PE01',
                'Running preboot checks for your application',
            ),
        ]

        succeeding_preboot_check_a.preboot.assert_called_once()
        succeeding_preboot_check_b.preboot.assert_called_once()
        assert exit_mock.called is False
        assert log_mock.call_args_list == expected_log_mock_call_args_list

    def test_run_preboot_checks_with_failing_one(self):
        """
        Ensure that the `run_preboot_checks` method prints the appropriate
        messages and that it exits with the appropriate exit code.
        """
        succeeding_preboot_check = mock.MagicMock()
        succeeding_preboot_check.preboot.return_value = True
        failing_preboot_check = mock.MagicMock()
        failing_preboot_check.preboot.return_value = (
            False, ('FB40', 'This fails lol'),
        )

        app = applications.ProcfileApplication(
            procfile=self.procfile,
            checks=[succeeding_preboot_check, failing_preboot_check],
        )

        with mock.patch('sys.exit') as exit_mock:
            with mock.patch('procenv.utils.log') as log_mock:
                app.run_preboot_checks()

        expected_log_mock_call_args_list = [
            mock.call(
                'PE01',
                'Running preboot checks for your application',
            ),
            mock.call(
                'FB40',
                'Check MagicMock.preboot() failed: This fails lol',
            ),
            mock.call(
                'PE11',
                'Exiting because at least one preboot check failed',
            ),
        ]

        succeeding_preboot_check.preboot.assert_called_once()
        failing_preboot_check.preboot.assert_called_once()
        exit_mock.assert_called_once_with(1)
        assert log_mock.call_args_list == expected_log_mock_call_args_list

    def test_setup_main_checks(self):
        """
        Ensure that the `setup_main_checks` method adds the `main_loop` tasks
        to the event loop of the application.
        """
        some_check = mock.MagicMock()
        self.app.loop = mock.MagicMock()
        self.app.checks = [some_check]

        self.app.setup_main_checks()

        self.app.loop.create_task.assert_called_once_with(
            some_check.main_loop.return_value,
        )

    def test_run_application(self):
        """
        Ensure that the `run_application` coroutine method creates the
        appropriate subprocess and awaits for it.
        """
        # The `sync_mock_process_wait` will help us capture the
        # call to the `wait` coroutine method, of the process returned by
        # `asyncio.create_subprocess_exec`, after we wrap it in a coroutine
        # function.
        sync_mock_process_wait = mock.MagicMock()

        async def mock_process_wait(*args, **kwargs):
            # Proxy the call to `sync_mock_process_wait`, to capture it.
            sync_mock_process_wait(*args, **kwargs)
            return True

        mock_process = mock.MagicMock()
        mock_process.wait = mock_process_wait

        # The `sync_mock_create_subprocess_exec` will help us capture the
        # call to `create_subprocess_exec`, after we wrap it in a coroutine
        # function.
        sync_mock_create_subprocess_exec = mock.MagicMock()

        async def mock_create_subprocess_exec(*args, **kwargs):
            # Proxy the call to `sync_mock_create_subprocess_exec`, to capture
            # it.
            sync_mock_create_subprocess_exec(*args, **kwargs)
            return mock_process

        with mock.patch(
            'asyncio.create_subprocess_exec', new=mock_create_subprocess_exec,
        ):
            run_application_coroutine = self.app.run_application()
            self.loop.run_until_complete(run_application_coroutine)

        sync_mock_create_subprocess_exec.assert_called_once_with(
            *self.app.cmd,
            stdout=sys.stdout, stderr=sys.stderr, loop=self.app.loop,
        )
        sync_mock_process_wait.assert_called_once_with()

    def test_run_and_wait_for_application(self):
        """
        Ensure that the `run_and_wait_for_application` runs the application's
        event loop, until the application completes.
        """
        loop_mock = mock.MagicMock()
        self.app.loop = loop_mock

        with mock.patch(
            'procenv.applications.ProcfileApplication.run_application',
        ) as run_application_mock:
            self.app.run_and_wait_for_application()

        loop_mock.run_until_complete.assert_called_once_with(
            run_application_mock.return_value,
        )
