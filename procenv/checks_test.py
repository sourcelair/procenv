from unittest import mock

from . import checks
from . import exceptions


def test_procfile_preboot_check():
    check = checks.ProcfileCheck()

    # Assert that when a Procfile is found, then `True` is being returned.
    with mock.patch(
        'procenv.utils.detect_procfile',
        return_value='Procfile.test',
    ) as detect_procfile_stub:
        assert check.preboot() == True
        detect_procfile_stub.assert_called_once_with()

    # Assert that when a Procfile is not found, then `False`, along with an
    # error message are being returned.
    with mock.patch('procenv.utils.detect_procfile', return_value=None):
        error_message = (
            'PF40',
            f'Cannot find a Procfile to run your application.',
        )
        assert check.preboot() == (False, error_message)


def test_database_url_preboot_check():
    check = checks.DatabaseURLCheck()

    # Assert that when the DATABASE_URL environment variable is available,
    # then the preboot check will log the appropriate informative message.
    with mock.patch('os.getenv', return_value='ledatabaseurl'):
        with mock.patch('procenv.utils.log') as log_stub:
            assert check.preboot() == True
            log_stub.assert_called_once_with(
                'DB10',
                'Your application is expected to connect to its database at '
                '"ledatabaseurl".',
            )

    # Assert that when the DATABASE_URL environment variable is not available,
    # then the preboot check will log nothing.
    with mock.patch('os.getenv', return_value=None):
        with mock.patch('procenv.utils.log') as log_stub:
            assert check.preboot() == True
            assert log_stub.called == False


def test_redis_url_preboot_check():
    check = checks.RedisURLCheck()

    # Assert that when the REDIS_URL environment variable is available,
    # then the preboot check will log the appropriate informative message.
    with mock.patch('os.getenv', return_value='leredis'):
        with mock.patch('procenv.utils.log') as log_stub:
            assert check.preboot() == True
            log_stub.assert_called_once_with(
                'RD10',
                'Your application is expected to connect to Redis at '
                '"leredis".',
            )

    # Assert that when the REDIS_URL environment variable is not available,
    # then the preboot check will log nothing.
    with mock.patch('os.getenv', return_value=None):
        with mock.patch('procenv.utils.log') as log_stub:
            assert check.preboot() == True
            assert log_stub.called == False



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
                f'"{checks.BaseCheck}".'
            )
            assert str(e) == expected_exception_message
