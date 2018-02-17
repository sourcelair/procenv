from unittest import mock

from . import checks
from . import exceptions


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
