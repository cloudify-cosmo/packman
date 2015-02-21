import logger
import utils
import re

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
        for module in modules:
            lgr.debug('installing module {0}'.format(module))
            utils.do('{0}/bin/pip --default-timeout={2} install {1}'.format(
                venv, module, timeout), attempts=attempts) \
                if venv else utils.do(
                    'pip --default-timeout={2} install {1}'.format(
                        venv, module, timeout), attempts=attempts)

    def get_modules(self, modules, dir=False, venv=False):
        """downloads python modules

        :param list modules: python modules to download
        :param string dir: dir to download modules to
        :param string venv: (optional) if ommited, will use system python
         else, will use `dir` (for virtualenvs and such)
        """
        for module in modules:
            lgr.debug('downloading module {0}'.format(module))
            return utils.do('{0}/pip install --no-use-wheel'
                            ' --download "{1}/" {2}'.format(
                                venv, dir, module)) \
                if venv else utils.do('pip install --no-use-wheel'
                                      ' --download "{0}/" {1}'.format(
                                          dir, module))

    def check_module_installed(self, name, dir=False):
        """checks to see that a module is installed

        :param string name: module to check for
        :param string dir: (optional) if ommited, will use system python
         else, will use `dir` (for virtualenvs and such)
        """
        lgr.debug('checking whether {0} is installed'.format(name))
        x = utils.do('pip freeze', capture=True) if not dir else \
            utils.do('{0}/pip freeze'.format(dir), capture=True)
        if re.search(r'{0}'.format(name), x.stdout):
            lgr.debug('module {0} is installed'.format(name))
            return True
        else:
            lgr.debug('module {0} is not installed'.format(name))
            return False

    # TODO: (FEAT) support virtualenv --relocate OR
    # TODO: (FEAT) support whack http://mike.zwobble.org/2013/09/relocatable-python-virtualenvs-using-whack/ # NOQA
    def venv(self, venv_dir):
        """creates a virtualenv

        :param string venv_dir: venv path to create
        """
        lgr.debug('creating virtualenv in {0}'.format(venv_dir))
        return utils.do('virtualenv {0}'.format(venv_dir))
