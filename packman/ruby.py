import logger
import sh
import sys
import codes

lgr = logger.init()


class Handler():
    def get_gems(self, gems, dir, rbenv=False):
        """downloads a list of ruby gems

        :param list gems: gems to download
        :param string dir: directory to download gems to
        """
        gem = sh.Command('{0}/bin/gem'.format(rbenv)) \
            if rbenv else sh.Command('gem')
        for gem in gems:
            lgr.debug('Downloading gem {0}'.format(gem))
            # TODO: (TEST) add support for ruby in different environments
            o = gem.install('--no-ri', '--no-rdoc', '--install-dir',
                            dir, gem, _iter=True)
            try:
                # this is where the command is actually executed
                for line in o:
                    lgr.debug(line)
            except:
                sys.exit(codes.mapping['failed_to_download_gem'])
