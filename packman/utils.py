from __future__ import with_statement  # only for python 2.5
import logging
import logger
import os
import contextlib
# import sh
import shutil
import time
# import fabric.api as fab
import errno
import sys
from functools import wraps
import platform

import codes

SUPPORTED_DISTROS = ('Ubuntu', 'debian', 'centos')
DEFAULT_BASE_LOGGING_LEVEL = logging.INFO
DEFAULT_VERBOSE_LOGGING_LEVEL = logging.DEBUG


# def do(command, attempts=2, sleep_time=3, accepted_err_codes=None,
#        capture=False, combine_stderr=False, sudo=False):
#     """executes a command locally with retries on failure.

#     if a `command` execution is successful, it will return a fabric
#     object with the output (x.stdout, x.stderr, x.succeeded, etc..)

#     else, it will retry an `attempts` number of attempts and if all fails
#     it will return the fabric output object.
#     obviously, `attempts` must be larger than 0...

#     :param string command: shell command to be executed
#     :param int attempts: number of attempts to perform on failure
#     :param int sleep_time: sleeptime between attempts
#     :param bool capture: should the output be captured for parsing?
#     :param bool combine_stderr: combine stdout and stderr (NOT YET IMPL)
#     :param bool sudo: run as sudo
#     :rtype: `responseObject` (for fabric operation)
#     """
#     if attempts < 1:
#         raise RuntimeError('attempts must be at least 1')
#     if not sleep_time > 0:
#         raise RuntimeError('sleep_time must be larger than 0')
#     if not accepted_err_codes:
#         accepted_err_codes = []

#     def _execute():
#         for execution in xrange(attempts):
#             with fab.settings(warn_only=True):
#                 with fab.hide('warnings'):
#                     x = fab.local('sudo {0}'.format(command), capture) \
#                         if sudo else fab.local(command, capture)
#                 if x.succeeded or x.return_code in accepted_err_codes:
#                     lgr.debug('successfully executed: ' + command)
#                     return x
#                 lgr.warning('failed to run command: {0} -retrying ({1}/{2})'
#                             .format(command, execution + 1, attempts))
#                 time.sleep(sleep_time)
#         lgr.error('failed to run command: {0} even after {1} attempts'
#                   ' with output: {2}'
#                   .format(command, execution, x.stdout))
#         return x

#     with fab.hide('running'):
#         return _execute()


def get_distro():
    """returns the machine's distro
    """
    return platform.dist()[0]


def check_distro(supported=SUPPORTED_DISTROS, verbose=False):
    """checks that the machine's distro is supported

    :param tuple supported: tuple of supported distros
    :param bool verbose: verbosity level
    """
    set_global_verbosity_level(verbose)
    distro = get_distro()
    lgr.debug('Distribution Identified: {0}'.format(distro))
    if distro not in supported:
        lgr.error('Your distribution is not supported.'
                  'Supported Disributions are:')
        for distro in supported:
            lgr.error('    {0}'.format(distro))
        sys.exit(codes.mapping['distro not supported'])


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


def retry(retries=4, delay_multiplier=3, backoff=2):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param int retries: number of times to try (not retry) before giving up
    :param int delay: initial delay between retries in seconds
    :param int backoff: backoff multiplier e.g. value of 2 will double the
     delay each retry
    """
    def retry_decorator(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            if retries < 0:
                raise ValueError('retries must be at least 0')
            if delay_multiplier <= 0:
                raise ValueError('delay_multiplier must be larger than 0')
            if backoff <= 1:
                raise ValueError('backoff must be greater than 1')
            mtries, mdelay = retries, delay_multiplier
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except SystemExit:
                    msg = "Retrying in {0} seconds...".format(mdelay)
                    lgr.warning(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry
    return retry_decorator


# # utils.execute(sh.ls, 3, 2, [0], '/var/log')
# def execute(func, attempts=1, sleep=3, accepted_err_codes=[0], *args):
#     if attempts < 1:
#         raise RuntimeError('Attempts must be at least 1')
#     if not sleep > 0:
#         raise RuntimeError('Sleep must be larger than 0')

#     for execution in xrange(attempts):
#         outcome = func(*args, _ok_code=accepted_err_codes)
#         if outcome.exit_code not in accepted_err_codes:
#             lgr.warning('Failed to execute: {0}'.format(func))
#             time.sleep(sleep)
#         else:
#             return outcome
#     lgr.error('Failed to run command even after {0} attempts'
#               ' with output: {1}'.format(execution, outcome))
#     sys.exit(codes.mapping['failed_to_execute_command'])


class Handler():
    """common class to handle files and directories
    """

    def mkdir(self, dir):
        """creates (recursively) a directory

        :param string dir: directory to create
        """
        if not os.path.isdir(dir):
            lgr.debug('Creating directory {0}'.format(dir))
            try:
                os.makedirs(dir)
            except OSError as ex:
                lgr.error('Failed to create {0} ({1})'.format(dir, str(ex)))
                sys.exit(codes.mapping['failed_to_mkdir'])
        else:
            lgr.debug('Directory already exists, skipping.')

    def rmdir(self, dir):
        """deletes a directory

        :param string dir: directory to remove
        """
        lgr.debug('Attempting to remove directory {0}'.format(dir))
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        else:
            lgr.debug('Dir doesn\'t exist')
            return False

    def rm(self, file):
        """deletes a file or a set of files
        :param string file(s): file(s) to remove
        """
        lgr.debug('removing files {0}'.format(file))
        if os.path.isfile(file):
            os.remove(file)
        else:
            lgr.debug('File(s) do(es)n\'t exist')
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
                return False

    def mv(self, src, dst):
        """moves files or directories

        :param string src: source to copy
        :param string dst: destination to copy to
        """
        lgr.debug('Moving {0} to {1}'.format(src, dst))
        return shutil.move(src, dst)

    # def tar(self, chdir, output_file, input_path):
    #     """tars an input file or directory

    #     :param string chdir: change to this dir before archiving
    #     :param string output_file: tar output file path
    #     :param string input: input path to create tar from
    #     :param string opts: tar opts
    #     """
    #     lgr.debug('tar-ing {0}'.format(output_file))
    #     return sh.tar('-czvf', output_file, input_path, C=chdir)

    # def untar(self, chdir, input_file, strip=0):
    #     """untars a file

    #     :param string chdir: change to this dir before extracting
    #     :param string input_file: file to untar
    #     :param string opts: tar opts
    #     """
    #     lgr.debug('untar-ing {0}'.format(input_file))
    #     return sh.tar('-xzvf', input_file, C=chdir, strip=strip)


lgr = logger.init()
