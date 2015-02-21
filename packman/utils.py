import logging
import logger
import os

import shutil
import time
import fabric.api as fab
import errno


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


class Handler():
    """common class to handle files and directories
    """

    def is_dir(self, dir):
        """checks if a directory exists

        :param string dir: directory to check
        :rtype: `bool`
        """
        lgr.debug('checking if {0} exists'.format(dir))
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
        lgr.debug('checking if {0} exists'.format(file))
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
        lgr.debug('creating directory {0}'.format(dir))
        return os.makedirs(dir) if not os.path.isdir(dir) \
            else lgr.debug('directory already exists, skipping.')
        return False

    def rmdir(self, dir):
        """deletes a directory

        :param string dir: directory to remove
        """
        lgr.debug('attempting to remove directory {0}'.format(dir))
        return shutil.rmtree(dir) \
            if os.path.isdir(dir) else lgr.debug('dir doesn\'t exist')
        return False

    # TODO: (IMPRV) handle multiple files differently
    # def rm(self, file):
    #     """deletes a file or a set of files

    #     :param string file(s): file(s) to remove
    #     """
    #     lgr.debug('removing files {0}'.format(file))
    #     return do('rm {0}'.format(file)) if os.path.isfile(file) \
    #         else lgr.debug('file(s) do(es)n\'t exist')
    #     return False

    def cp(self, src, dst):
        """copies (recuresively or not) files or directories

        :param string src: source to copy
        :param string dst: destination to copy to
        :param bool recurse: should the copying process be recursive?
        """
        lgr.debug('copying {0} to {1}'.format(src, dst))
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
        lgr.debug('moving {0} to {1}'.format(src, dst))
        return shutil.move(src, dst)

    def tar(self, chdir, output_file, input_path, opts='zvf'):
        """tars an input file or directory

        :param string chdir: change to this dir before archiving
        :param string output_file: tar output file path
        :param string input: input path to create tar from
        :param string opts: tar opts
        """
        lgr.debug('tar-ing {0}'.format(output_file))
        return do('tar -C {0} -c{1} {2} {3}'.format(
            chdir, opts, output_file, input_path))

    def untar(self, chdir, input_file, opts='zvf', strip=0):
        """untars a file

        :param string chdir: change to this dir before extracting
        :param string input_file: file to untar
        :param string opts: tar opts
        """
        lgr.debug('untar-ing {0}'.format(input_file))
        return do('tar -C {0} -x{1} {2} --strip={3}'.format(
            chdir, opts, input_file, strip))


lgr = logger.init()
