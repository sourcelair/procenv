from unittest import mock
import os

from . import utils


def test_log_message():
    with mock.patch('sys.stderr') as stderr_mock:
        utils.log('hey')
        stderr_mock.write.assert_called_once_with('[Procenv Message] hey\n')

    with mock.patch('sys.stderr') as stderr_mock:
        utils.log('ho', 'T0')
        stderr_mock.write.assert_called_once_with(
            '[Procenv Message] (T0) ho\n',
        )


def test_detect_procfile():
    cwd = os.getcwd()

    # Assert that calling `detect_procfile` in a directory without a file
    # named `Procfile` and without the `PROCFILE` environment variable set,
    # `None` is returned.
    os.chdir(os.path.join(cwd, 'procenv/fixtures/procfile_scum'))
    utils.detect_procfile.cache_clear()
    assert utils.detect_procfile() == None

    # Assert that calling `detect_procfile` in a directory with the `PROCFILE`
    # environment variable set and the file not existing, and no file named
    # `Procfile` exists in that directory, `None` is returned.
    os.chdir(os.path.join(cwd, 'procenv/fixtures/procfile_scum'))
    utils.detect_procfile.cache_clear()
    with mock.patch('os.getenv', return_value='Procfile.dev'):
        assert utils.detect_procfile() == None

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
