import asyncio
import sys

from . import utils


class ProcfileApplication:
    """
    The `ProcfileApplication` class helps run, monitor and manage a
    Procfile-based application in an asyncio event loop.
    """

    def __init__(self, procfile, checks, loop=None):
        self.procfile = procfile
        self.checks = checks
        self.loop = loop or asyncio.get_event_loop()

    @property
    def cmd(self):
        return ['honcho', '-f', self.procfile, 'start']

    @property
    def preboot_checks(self):
        _checks = [
            check for check in self.checks if hasattr(check, 'preboot')
        ]
        return _checks

    @property
    def main_checks(self):
        _checks = [
            check for check in self.checks if hasattr(check, 'main')
        ]
        return _checks

    def run_preboot_checks(self):
        utils.log('PE01', 'Running preboot checks for your application')
        at_least_one_check_has_failed = False

        for check in self.preboot_checks:
            preboot_result = check.preboot()

            if (type(preboot_result) == tuple):
                succeedded, reason = preboot_result
            else:
                succeedded = preboot_result
                reason = None

            if not succeedded:
                at_least_one_check_has_failed = True

                if reason:
                    code, message = reason
                    message = (
                        f'Check {check.__class__.__name__}.preboot() failed: '
                        f'{message}'
                    )
                else:
                    message = reason
                    code = 'PE40'

                utils.log(code, message)

        if at_least_one_check_has_failed:
            utils.log(
                'PE11', 'Exiting because at least one preboot check failed',
            )
            sys.exit(1)

    def setup_main_checks(self):
        for check in self.main_checks:
            self.loop.create_task(check.main_loop())

    async def run_application(self):
        utils.log(
            'PE10',
            f'Running application with Procfile "{self.procfile}"',
        )
        process = await asyncio.create_subprocess_exec(
            *self.cmd, stdout=sys.stdout, stderr=sys.stderr, loop=self.loop,
        )
        await process.wait()

    def run_and_wait_for_application(self):
        self.loop.run_until_complete(self.run_application())
