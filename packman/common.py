import logging
import logging.config

import packman_config as pkm_conf

from time import sleep
from fabric.api import *  # NOQA
import os
import sys

DEFAULT_BASE_LOGGING_LEVEL = logging.INFO
DEFAULT_VERBOSE_LOGGING_LEVEL = logging.DEBUG


def init_logger(base_level=DEFAULT_BASE_LOGGING_LEVEL,
                verbose_level=DEFAULT_VERBOSE_LOGGING_LEVEL,
                logging_config=None):
    """initializes a base logger

    you can use this to init a logger in any of your files.
    this will use config.py's LOGGER param and logging.dictConfig to configure
    the logger for you.

    :param int|logging.LEVEL base_level: desired base logging level
    :param int|logging.LEVEL verbose_level: desired verbose logging level
    :param dict logging_dict: dictConfig based configuration.
     used to override the default configuration from config.py
    :rtype: `python logger`
    """
    if logging_config is None:
        logging_config = {}
    logging_config = logging_config or pkm_conf.LOGGER
    # TODO: (IMPRV) only perform file related actions if file handler is
    # TODO: (IMPRV) defined.

    log_dir = os.path.expanduser(
        os.path.dirname(
            pkm_conf.LOGGER['handlers']['file']['filename']))
    if os.path.isfile(log_dir):
        sys.exit('file {0} exists - log directory cannot be created '
                 'there. please remove the file and try again.'
                 .format(log_dir))
    try:
        logfile = pkm_conf.LOGGER['handlers']['file']['filename']
        d = os.path.dirname(logfile)
        if not os.path.exists(d) and not len(d) == 0:
            os.makedirs(d)
        logging.config.dictConfig(logging_config)
        lgr = logging.getLogger('user')
        # lgr.setLevel(base_level) if not pkm_conf.VERBOSE \
        lgr.setLevel(base_level)
        return lgr
    except ValueError as e:
        sys.exit('could not initialize logger.'
                 ' verify your logger config'
                 ' and permissions to write to {0} ({1})'
                 .format(logfile, e))


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
            with settings(warn_only=True):
                with hide('warnings'):
                    x = local('sudo {0}'.format(command), capture) if sudo \
                        else local(command, capture)
                if x.succeeded or x.return_code in accepted_err_codes:
                    lgr.debug('successfully executed: ' + command)
                    return x
                lgr.warning('failed to run command: {0} -retrying ({1}/{2})'
                            .format(command, execution + 1, attempts))
                sleep(sleep_time)
        lgr.error('failed to run command: {0} even after {1} attempts'
                  ' with output: {2}'
                  .format(command, execution, x.stdout))
        return x

    with hide('running'):
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
    # print 'level is: ' + str(lgr.getEffectiveLevel())


lgr = init_logger()
