import os
import utils
import retrieve
import logger

lgr = logger.init()


class Handler(utils.Handler, retrieve.Handler):
    @staticmethod
    def update():
        """runs yum update
        """
        lgr.debug('updating local yum repo')
        return utils.do('sudo yum update')

    def check_if_package_is_installed(self, package):
        """checks if a package is installed

        :param string package: package name to check
        :rtype: `bool` representing whether package is installed or not
        """

        lgr.debug('checking if {0} is installed'.format(package))
        x = utils.do('sudo rpm -qa | grep {0}'.format(
            package), attempts=1, accepted_err_codes=[1])
        if x.return_code == 0:
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
            # TODO: (TEST) run yum reinstall instead of yum install.
            lgr.debug('downloading {0} to {1}'.format(req, sources_path))
            # TODO: (FIX) yum download exits with an error even if the download
            # TODO: (FIX) succeeded due to a non-zero error message.
            # TODO: (FEAT) add yum enable-repo option
            # TODO: (IMPRV) $(repoquery --requires --recursive --resolve pkg)
            # TODO: (IMPRV) can be used to download deps.
            # TODO: (IMPRV) test to see if it works.
            # if self.check_if_package_is_installed(package):
            # return do('sudo yum -y reinstall --downloadonly '
            #           '--downloaddir={1}/archives {0}'.format(
            #               package, dir), accepted_err_codes=[1])
            # else:
            utils.do('sudo yum -y install --downloadonly '
                     '--downloaddir={1}/archives {0}'.format(
                         req, sources_path), accepted_err_codes=[1])

    def install(self, packages):
        """yum installs a list of packages

        :param list package: packages to install
        """
        for package in packages:
            lgr.debug('installing {0}'.format(package))
            utils.do('sudo yum -y install {0}'.format(package))

    def add_src_repos(self, source_repos):
        """adds a list of source repos to the apt repo

        :param list source_repos: repos to add to sources list
        """
        for source_repo in source_repos:
            lgr.debug('adding source repository {0}'.format(source_repo))
            if os.path.splitext(source_repo)[1] == '.rpm':
                utils.do('sudo rpm -ivh {0}'.format(
                    source_repo), accepted_err_codes=[1])
            else:
                self.download(source_repo, dir='/etc/yum.repos.d/')

    def add_key(self, key_file):
        """adds a list of keys to the local repo

        :param string key_files: key files paths
        """
        lgr.debug('adding key {0}'.format(key_file))
        utils.do('sudo rpm --import {0}'.format(key_file))
