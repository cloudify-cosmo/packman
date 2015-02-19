import utils
import exceptions
import logger
import os

lgr = logger.init()


class Handler(utils.Handler):
    def downloads(self, urls, dir=False, sudo=True):
        """wgets a list of urls to a destination directory

        :param list urls: a list of urls to download
        :param string dir: download to dir...
        """
        for source_url in urls:
            url_ext = os.path.splitext(source_url)[1]
            # if the source file is an rpm or deb, we want to download
            # it to the archives folder. yes, it's a dreadful solution...
            if url_ext in ('.rpm', '.deb'):
                lgr.debug('the file is a {0} file. we\'ll download it '
                          'to the archives folder'.format(url_ext))
                self.download(source_url, dir=os.path.join(
                    dir, 'archives'))
            else:
                self.download(source_url, dir=dir)

    def download(self, url, dir=False, file=False, sudo=False):
        options = '--timeout=30'
        # workaround for archives folder
        if (file and dir) or (not file and not dir):
            lgr.warning('please specify either a directory'
                        ' or file to download to.')
            raise exceptions.PackagerError('please specify either a directory'
                                           ' or file to download to.')
        lgr.debug('downloading {0} to {1}'.format(url, file or dir))
        return utils.do('wget {0} {1} -O {2}'.format(
            url, options, file), sudo=sudo) \
            if file else utils.do('wget {0} {1} -P {2}'.format(
                url, options, dir), sudo=sudo)
