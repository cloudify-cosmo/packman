import utils
import logger
import exceptions as exc

lgr = logger.init()


class AptHandler(utils.Handler):
    def dpkg_name(self, dir):
        """renames deb files to conventional names

        :param string dir: dir to review
        """

        lgr.debug('renaming deb files...')
        return utils.do('dpkg-name {0}/*.deb'.format(dir))

    def check_if_package_is_installed(self, package):
        """checks if a package is installed

        :param string package: package name to check
        :rtype: `bool` representing whether package is installed or not
        """

        lgr.debug('checking if {0} is installed'.format(package))
        x = utils.do('sudo dpkg -s {0}'.format(package), attempts=1)
        if x.succeeded:
            lgr.debug('{0} is installed'.format(package))
            return True
        else:
            lgr.error('{0} is not installed'.format(package))
            return False

    def download(self, reqs, sources_path):
        """downloads component requirements

        :param list reqs: list of requirements to download
        :param sources_path: path to download requirements to
        """
        for req in reqs:
            # TODO: (TEST) add an is-package-installed check. if it is
            # TODO: (TEST) run apt-get install --reinstall instead of apt-get
            # TODO: (TEST) install.
            # TODO: (IMPRV) try http://askubuntu.com/questions/219828/getting-deb-package-dependencies-for-an-offline-ubuntu-computer-through-windows  # NOQA
            # TODO: (IMPRV) for downloading requirements
            lgr.debug('downloading {0} to {1}'.format(req, sources_path))
            # if self.check_if_package_is_installed(package):
            utils.do('sudo apt-get -y install {0} -d -o=dir::cache={1}'.format(
                req, sources_path))
            # else:
            #     return do('sudo apt-get -y install --reinstall '
            #               '{0} -d -o=dir::cache={1}'.format(pkg, dir))

    def autoremove(self, pkg):
        """autoremoves package dependencies

        :param string pkg: package to remove
        """
        lgr.debug('removing unnecessary dependencies...')
        return utils.do('sudo apt-get -y autoremove {0}'.format(pkg))

    def add_src_repos(self, source_repos):
        """adds a list of source repos to the apt repo

        :param list source_repos: repos to add to sources list
        """
        for source_repo in source_repos:
            lgr.debug('adding source repository {0}'.format(source_repo))
            utils.do('sudo sed -i "2i {0}" /etc/apt/sources.list'.format(
                source_repo))

    def add_ppa_repos(self, source_ppas, debian, distro):
        """adds a list of ppa repos to the apt repo

        :param list source_ppas: ppa urls to add
        """
        if source_ppas and not debian:
            raise exc.PackagerError('ppas not supported by {0}'.format(distro))
        for source_ppa in source_ppas:
            lgr.debug('adding ppa repository {0}'.format(source_ppa))
            utils.do('add-apt-repository -y {0}'.format(source_ppa))
        if source_ppas:
            self.update()

    def add_key(self, key_file):
        """adds a list of keys to the local repo

        :param string key_files: key files paths
        """
        lgr.debug('adding key {0}'.format(key_file))
        return utils.do('sudo apt-key add {0}'.format(key_file))

    def update(self):
        """runs apt-get update
        """
        lgr.debug('updating local apt repo')
        return utils.do('sudo apt-get update')

    def install(self, packages):
        """apt-get installs a list of packages

        :param list packages: packages to install
        """
        for package in packages:
            lgr.debug('installing {0}'.format(package))
            utils.do('sudo apt-get -y install {0}'.format(package))

    def purge(self, packages):
        """completely purges a list of packages from the local repo

        :param list packages: packages name to purge
        """
        for package in packages:
            lgr.debug('attemping to purge {0}'.format(package))
            utils.do('sudo apt-get -y purge {0}'.format(package))
