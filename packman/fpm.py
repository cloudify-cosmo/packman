import utils
import logger
import os
import sh

lgr = logger.init()


class Handler(utils.Handler):
    """fpm handler to handle the packaging process
    """
    def __init__(self, name, input_type, output_type, source):
        self.name = name
        output_type = 'tar' if output_type.startswith('tar') \
            else output_type
        input_type = input_type
        self.source = source
        self.command = sh.fpm.bake(n=name, s=input_type, t=output_type)

    def _build_cmd_string(self, **fpm_params):
        """this will build an fpm command string
        """
        # TODO: add verbose mode to fpm runs
        if fpm_params.get('version'):
            self.command = self.command.bake(v=fpm_params['version'])
        if fpm_params.get('chdir'):
            self.command = self.command.bake(C=fpm_params['chdir'])
        if fpm_params.get('after_install'):
            self.command = self.command.bake(
                '--after-install', os.path.abspath(
                    fpm_params['after_install']))
        if fpm_params.get('before_install'):
            self.command = self.command.bake(
                '--before-install', os.path.abspath(
                    fpm_params['before_install']))
        if fpm_params.get('depends'):
            for depend in fpm_params['depends']:
                self.command = self.command.bake(d=depend)
        if fpm_params.get('force'):
            self.command = self.command.bake('-f')
        # MUST BE LAST
        self.command = self.command.bake(self.source)
        lgr.debug('fpm cmd is: {0}'.format(self.command))
        return self.command

    def execute(self, **fpm_params):
        """runs fpm
        """
        self._build_cmd_string(**fpm_params)
        return self.command()
