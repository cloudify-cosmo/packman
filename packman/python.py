import logger
import utils
import re
import sh
import sys
import codes

lgr = logger.init()


class Handler(utils.Handler):
    """python operations handler
    """
    def install(self, modules, venv=False, attempts=5, timeout='45'):
        """pip installs a list of modules

        :param list modules: python modules to ``pip install``
        :param string venv: (optional) if ommited, will use system python
         else, will use `venv` (for virtualenvs and such)
        """
        pip = sh.Command('{0}/bin/pip'.format(venv)) \
            if venv else sh.Command('pip')
        for module in modules:
            lgr.debug('Installing module {0}'.format(module))
            o = pip.install('--default-timeout', timeout, module, _iter=True)
            for line in o:
                lgr.debug(line)
            installed = self.check_module_installed(module, venv)
            if not installed:
                lgr.error('Modules {0} could not be installed.'.format(module))
                sys.exit(codes.mapping['module_could_not_be_installed'])

    @utils.retry(retries=2, delay=3)
    def get_modules(self, modules, dir=False, venv=False, timeout='45'):
        """downloads python modules

        :param list modules: python modules to download
        :param string dir: dir to download modules to
        :param string venv: (optional) if ommited, will use system python
         else, will use `dir` (for virtualenvs and such)
        """
        pip = sh.Command('{0}/bin/pip'.format(venv)) \
            if venv else sh.Command('pip')
        for module in modules:
            # returns a stream of the command
            o = pip.install(
                '--no-use-wheel', '--download', dir, module, _iter=True)
            try:
                # this is where the command is actually executed
                for line in o:
                    lgr.debug(line)
            except:
                sys.exit('Failed to download module: {0}'.format(module))

    def check_module_installed(self, name, venv=False):
        """checks to see that a module is installed

        :param string name: module to check for
        :param string venv: (optional) if ommited, will use system python
         else, will use `venv` (for virtualenvs and such)
        """
        pip = sh.Command('{0}/bin/pip'.format(venv)) \
            if venv else sh.Command('pip')
        lgr.debug('Checking whether {0} is installed'.format(name))
        installed_modules = pip.freeze()
        if re.search(r'{0}'.format(name), installed_modules):
            lgr.debug('Module {0} is installed'.format(name))
            return True
        else:
            lgr.debug('Module {0} is not installed'.format(name))
            return False

    # TODO: (FEAT) support virtualenv --relocate OR
    # TODO: (FEAT) support whack http://mike.zwobble.org/2013/09/relocatable-python-virtualenvs-using-whack/ # NOQA
    def venv(self, venv_dir):
        """creates a virtualenv

        :param string venv_dir: venv path to create
        """
        lgr.debug('creating virtualenv in {0}'.format(venv_dir))
        return sh.virtualenv(venv_dir)
