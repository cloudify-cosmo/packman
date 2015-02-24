from __future__ import with_statement  # only for python 2.5
import logging
import logger
import os
import contextlib
import sh
import shutil
import time
import fabric.api as fab
import errno
import sys

import codes

DEFAULT_BASE_LOGGING_LEVEL = logging.INFO
DEFAULT_VERBOSE_LOGGING_LEVEL = logging.DEBUG


def do(command, attempts=2, sleep_time=3, accepted_err_codes=None,
       capture=False, combine_stderr=False, sudo=False):
    """executes a command locally with retries on failure.

    if a `command` execution is successful, it will return a fabric
    object with the output (x.stdout, x.stderr, x.succeeded, etc..)

    else, it will retry an `attempts` number of attempts and if all fails
    it will return the fabric output object.
    obviously, `attempts` must be larger than 0...

    :param string command: shell command to be executed
    :param int attempts: number of attempts to perform on failure
    :param int sleep_time: sleeptime between attempts
    :param bool capture: should the output be captured for parsing?
    :param bool combine_stderr: combine stdout and stderr (NOT YET IMPL)
    :param bool sudo: run as sudo
    :rtype: `responseObject` (for fabric operation)
    """
    if attempts < 1:
        raise RuntimeError('attempts must be at least 1')
    if not sleep_time > 0:
        raise RuntimeError('sleep_time must be larger than 0')
    if not accepted_err_codes:
        accepted_err_codes = []

    def _execute():
        for execution in xrange(attempts):
            with fab.settings(warn_only=True):
                with fab.hide('warnings'):
                    x = fab.local('sudo {0}'.format(command), capture) \
                        if sudo else fab.local(command, capture)
                if x.succeeded or x.return_code in accepted_err_codes:
                    lgr.debug('successfully executed: ' + command)
                    return x
                lgr.warning('failed to run command: {0} -retrying ({1}/{2})'
                            .format(command, execution + 1, attempts))
                time.sleep(sleep_time)
        lgr.error('failed to run command: {0} even after {1} attempts'
                  ' with output: {2}'
                  .format(command, execution, x.stdout))
        return x

    with fab.hide('running'):
        return _execute()


def set_global_verbosity_level(is_verbose_output=False):
    """sets the global verbosity level for console and the lgr logger.

    :param bool is_verbose_output: should be output be verbose
    """
    global verbose_output
    verbose_output = is_verbose_output
    if verbose_output:
        lgr.setLevel(logging.DEBUG)
    else:
        lgr.setLevel(logging.INFO)


@contextlib.contextmanager
def chdir(dirname=None):
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
            yield
    finally:
        os.chdir(curdir)


# utils.execute(sh.ls, 3, 2, [0], '/var/log')
def execute(func, attempts=1, sleep=3, accepted_err_codes=[0], *args):
    if attempts < 1:
        raise RuntimeError('Attempts must be at least 1')
    if not sleep > 0:
        raise RuntimeError('Sleep must be larger than 0')

    for execution in xrange(attempts):
        outcome = func(*args, _ok_code=accepted_err_codes)
        if outcome.exit_code not in accepted_err_codes:
            lgr.warning('Failed to execute: {0}'.format(func))
            time.sleep(sleep)
        else:
            return outcome
    lgr.error('Failed to run command even after {0} attempts'
              ' with output: {1}'.format(execution, outcome))
    sys.exit(codes.mapping['failed_to_execute_command'])


class Handler():
    """common class to handle files and directories
    """

    def is_dir(self, dir):
        """checks if a directory exists

        :param string dir: directory to check
        :rtype: `bool`
        """
        lgr.debug('Checking whether {0} exists'.format(dir))
        if os.path.isdir(dir):
            lgr.debug('{0} exists'.format(dir))
            return True
        else:
            lgr.debug('{0} does not exist'.format(dir))
            return False

    def is_file(self, file):
        """checks if a file exists

        :param string file: file to check
        :rtype: `bool`
        """
        lgr.debug('Checking Whether {0} exists'.format(file))
        if os.path.isfile(file):
            lgr.debug('{0} exists'.format(file))
            return True
        else:
            lgr.debug('{0} does not exist'.format(file))
            return False

    def mkdir(self, dir):
        """creates (recursively) a directory

        :param string dir: directory to create
        """
        lgr.debug('Creating directory {0}'.format(dir))
        return os.makedirs(dir) if not os.path.isdir(dir) \
            else lgr.debug('Directory already exists, skipping.')
        return False

    def rmdir(self, dir):
        """deletes a directory

        :param string dir: directory to remove
        """
        lgr.debug('Attempting to remove directory {0}'.format(dir))
        return shutil.rmtree(dir) \
            if os.path.isdir(dir) else lgr.debug('Dir doesn\'t exist')
        return False

    def cp(self, src, dst):
        """copies (recuresively or not) files or directories

        :param string src: source to copy
        :param string dst: destination to copy to
        :param bool recurse: should the copying process be recursive?
        """
        lgr.debug('Copying {0} to {1}'.format(src, dst))
        try:
            shutil.copytree(src, dst)
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                lgr.error('Copying failed. Error: {0}'.format(e))

    def mv(self, src, dst):
        """moves files or directories

        :param string src: source to copy
        :param string dst: destination to copy to
        """
        lgr.debug('Moving {0} to {1}'.format(src, dst))
        return shutil.move(src, dst)

    def tar(self, chdir, output_file, input_path):
        """tars an input file or directory

        :param string chdir: change to this dir before archiving
        :param string output_file: tar output file path
        :param string input: input path to create tar from
        :param string opts: tar opts
        """
        lgr.debug('tar-ing {0}'.format(output_file))
        return sh.tar('-czvf', output_file, input_path, C=chdir)

    def untar(self, chdir, input_file, strip=0):
        """untars a file

        :param string chdir: change to this dir before extracting
        :param string input_file: file to untar
        :param string opts: tar opts
        """
        lgr.debug('untar-ing {0}'.format(input_file))
        return sh.tar('-xzvf', input_file, C=chdir, strip=strip)


lgr = logger.init()
