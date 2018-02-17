from unittest import mock
import os

from . import checks
from . import utils


def test_detect_procfile():
    """
    This test asserts that `detect_procfile` returns the appropriate
    `Procfile` (if it does exist), by taking into account the `PROCFILE`
    environment variable. If no Procfile exists, then `None` should be
    returned.
    """
    cwd = os.getcwd()

    # Assert that calling `detect_procfile` in a directory without a file
    # named `Procfile` and without the `PROCFILE` environment variable set,
    # `None` is returned.
    os.chdir(os.path.join(cwd, 'procenv/fixtures/procfile_scum'))
    utils.detect_procfile.cache_clear()
    assert utils.detect_procfile() is None

    # Assert that calling `detect_procfile` in a directory with the `PROCFILE`
    # environment variable set and the file not existing, and no file named
    # `Procfile` exists in that directory, `None` is returned.
    os.chdir(os.path.join(cwd, 'procenv/fixtures/procfile_scum'))
    utils.detect_procfile.cache_clear()
    with mock.patch('os.getenv', return_value='Procfile.dev'):
        assert utils.detect_procfile() is None

    # Assert that calling `detect_procfile` in a directory with a file named
    # `Procfile` in it and without the `PROCFILE` environment variable set,
    # `"Procfile"` is returned.
    os.chdir(os.path.join(cwd, 'procenv/fixtures/procfile_dev'))
    utils.detect_procfile.cache_clear()
    assert utils.detect_procfile() == 'Procfile'

    # Assert that calling `detect_procfile` in a directory with the `PROCFILE`
    # environment variable set and the file existing, the value of `PROCFILE`
    # is returned.
    os.chdir(os.path.join(cwd, 'procenv/fixtures/procfile_dev'))
    utils.detect_procfile.cache_clear()
    with mock.patch('os.getenv', return_value='Procfile.dev'):
        assert utils.detect_procfile() == 'Procfile.dev'

    # Assert that calling `detect_procfile` in a directory with the `PROCFILE`
    # environment variable set and the file existing, if a file named
    # `Procfile` exists, it is being returned as fallback.
    os.chdir(os.path.join(cwd, 'procenv/fixtures/procfile_dev'))
    utils.detect_procfile.cache_clear()
    with mock.patch('os.getenv', return_value='Procfile.scum'):
        assert utils.detect_procfile() == 'Procfile'

    os.chdir(cwd)


def test_import_string():
    """
    Make sure that `import_string` imports the appropriate module or class,
    when invoked.
    """
    # Assert that importing a module via a dotted path, works
    assert utils.import_string('procenv.checks') == checks

    # Assert that importing a class from a module via a dotted path, works
    assert utils.import_string('procenv.checks.BaseCheck') == checks.BaseCheck

    # Assert that attemting to import a module or class via a not a dotted
    # path, raises the appropriate error.
    try:
        utils.import_string('scum')
    except ImportError as e:
        assert str(e) == 'scum doesn\'t look like a module path'

    # Assert that attemting to import a dotted path that cannot be resolved
    # to a module or class or module attribute, raises the appropriate error.
    try:
        utils.import_string('procenv.checks.InexistentCheck')
    except ImportError as e:
        expected_exception_message = (
            'Module "procenv.checks" does not define a "InexistentCheck"'
            'attribute/class'
        )
        assert str(e) == expected_exception_message


def test_log_message():
    """
    This test makes sure that `log` writes Procenv Messages to STDERR in the
    appropriate format. Logging is important in Procenv, we do not want to
    ruin it.
    """
    with mock.patch('sys.stderr') as stderr_mock:
        utils.log('PE99', 'Hey mark')
        stderr_mock.write.assert_called_once_with(
            '[Procenv Message] (PE99) Hey mark\n',
        )
