import utils
import os
import logger

lgr = logger.init()


class Handler(utils.Handler):
    """fpm handler to handle the packaging process
    """
    def __init__(self, name, input_type, output_type, source):
        self.name = name
        self.output_type = 'tar' if output_type.startswith('tar') \
            else output_type
        self.input_type = input_type
        self.source = source
        self.command = 'fpm -n {0} -s {1} -t {2} '

    def _build_cmd_string(self, **kwargs):
        """this will build a command string
        """
        # TODO: add verbose mode to fpm runs
        self.command = self.command.format(
            self.name, self.input_type, self.output_type)
        if kwargs.get('version'):
            self.command += '-v {0} '.format(kwargs['version'])
        if kwargs.get('chdir'):
            self.command += '-C {0} '.format(kwargs['chdir'])
        if kwargs.get('after_install'):
            self.command += '--after-install {0} '.format(
                os.path.join(os.getcwd(), kwargs['after_install']))
        if kwargs.get('before_install'):
            self.command += '--before-install {0} '.format(
                os.path.join(os.getcwd(), kwargs['before_install']))
        if kwargs.get('depends'):
            self.command += "-d " + " -d ".join(kwargs['depends'])
            self.command += " "
        if kwargs.get('force'):
            self.command += '-f '
        # MUST BE LAST
        self.command += self.source
        lgr.debug('fpm cmd is: {0}'.format(self.command))

    def execute(self, **kwargs):
        """runs fpm
        """
        self._build_cmd_string(**kwargs)
        utils.do(self.command)
