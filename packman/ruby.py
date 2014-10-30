import utils
import logger

lgr = logger.init()


class RubyHandler(utils.Handler):
    def get_gems(self, gems, rbenv=False, dir=False):
        """downloads a list of ruby gems

        :param list gems: gems to download
        :param string dir: directory to download gems to
        """
        for gem in gems:
            lgr.debug('downloading gem {0}'.format(gem))
            # TODO: (TEST) add support for ruby in different environments
            utils.do('sudo {0}/bin/gem install --no-ri --no-rdoc'
                     ' --install-dir {1} {2}'.format(rbenv, dir, gem)) \
                if rbenv else utils.do('sudo gem install --no-ri --no-rdoc'
                                       ' --install-dir {1} {2}'.format(
                                           dir, gem))
