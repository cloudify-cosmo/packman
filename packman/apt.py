import utils
import logger

import re
import urllib2
import os
import sh

lgr = logger.init()


class Handler(utils.Handler):
    def dpkg_name(self, dir):
        """renames deb files to conventional names

        :param string dir: dir to review
        """

        lgr.debug('Renaming deb files...')
        return sh.dpkg_name('{0}/*.deb'.format(dir))

    def check_if_package_is_installed(self, package):
        """checks if a package is installed

        :param string package: package name to check
        :rtype: `bool` representing whether package is installed or not
        """
        lgr.debug('Checking if {0} is installed'.format(package))
        o = sh.dpkg('-s', package)

        if not o.exit_code:
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
            lgr.debug('Downloading {0} to {1}...'.format(req, sources_path))
            o = sh.apt_get.install('-y', req, '-d', o='dir::cache={0}'.format(
                sources_path), _iter=True)
            for line in o:
                lgr.debug(line)
            sh.rm('{0}/*.bin'.format(sources_path))

    def autoremove(self, pkg):
        """autoremoves package dependencies

        :param string pkg: package to remove
        """
        lgr.debug('Removing unnecessary dependencies...')
        return sh.apt_get.autoremove('-y', pkg)

    def add_src_repos(self, source_repos):
        """adds a list of source repos to the apt repo

        :param list source_repos: repos to add to sources list
        """
        def add(source_repo, f, apt_file):
            if not re.search(source_repo, f.read()):
                lgr.debug('Adding source repository {0}'.format(source_repo))
                sh.sed('-i', "2i {0}".format(source_repo), apt_file)
            else:
                lgr.debug('Repo {0} already added.'.format(source_repo))

        apt_file = '/etc/apt/sources.list'
        for source_repo in source_repos:
            with open(apt_file) as f:
                add(source_repo, f, apt_file)

    def add_ppa_repos(self, source_ppas):
        """adds a list of ppa repos to the apt repo

        :param list source_ppas: ppa urls to add
        """
        for source_ppa in source_ppas:
            lgr.debug('Adding ppa repository {0}'.format(source_ppa))
            sh.add_apt_repository('-y', source_ppa)
        if source_ppas:
            self.update()

    def add_keys(self, key_files, sources_path):
        """adds a list of keys to the local repo

        :param string key_files: key files paths
        """
        for key in key_files:
            key_file = urllib2.unquote(key).decode('utf8').split('/')[-1]
            self.add_key(os.path.join(sources_path, key_file))

    def add_key(self, key_file):
        """adds a of keys to the local repo

        :param string key_file: key file path
        """
        lgr.debug('Adding key {0}'.format(key_file))
        return sh.apt_key.add(key_file)

    def update(self):
        """runs apt-get update
        """
        lgr.debug('Updating local apt repo')
        return sh.apt_get.update()

    def install(self, packages):
        """apt-get installs a list of packages

        :param list packages: packages to install
        """
        for package in packages:
            lgr.debug('Installing {0}'.format(package))
            sh.apt_get.install('-y', package)

    def purge(self, packages):
        """completely purges a list of packages from the local repo

        :param list packages: packages name to purge
        """
        for package in packages:
            lgr.debug('Attemping to purge {0}'.format(package))
            sh.apt_get.purge('-y', package)
