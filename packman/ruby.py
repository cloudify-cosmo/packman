import utils
import logger

lgr = logger.init()


class Handler(utils.Handler):
    def get_gems(self, gems, dir, rbenv=False):
        """downloads a list of ruby gems

        :param list gems: gems to download
        :param string dir: directory to download gems to
        """
        for gem in gems:
            lgr.debug('Downloading gem {0}'.format(gem))
            # TODO: (TEST) add support for ruby in different environments
            if rbenv:
                utils.do('{0}/bin/gem install --no-ri --no-rdoc'
                         ' --install-dir {1} {2}'.format(rbenv, dir, gem))
            else:
                utils.do('gem install --no-ri --no-rdoc'
                         ' --install-dir {0} {1}'.format(dir, gem))
