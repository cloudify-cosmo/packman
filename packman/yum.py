import os
import retrieve
import logger
import sh

lgr = logger.init()


class Handler(retrieve.Handler):
    @staticmethod
    def update():
        """runs yum update
        """
        lgr.debug('Updating local yum repo')
        return sh.yum.update()

    def check_if_package_is_installed(self, package):
        """checks if a package is installed

        :param string package: package name to check
        :rtype: `bool` representing whether package is installed or not
        """

        lgr.debug('Checking if {0} is installed'.format(package))
        r = sh.grep(sh.rpm('-qa', _ok_code=[0, 1]), package)
        if r.exit_code == 0:
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
            lgr.debug('Downloading {0} to {1}...'.format(req, sources_path))
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
            o = sh.yum.install(
                '-y', req, '--downloadonly', downloaddir=os.path.join(
                    sources_path, 'archives'), _iter=True, _ok_code=[0, 1])
            for line in o:
                lgr.debug(line)

    def install(self, packages):
        """yum installs a list of packages

        :param list package: packages to install
        """
        for package in packages:
            lgr.debug('Installing {0}'.format(package))
            sh.yum.install('-y', package)

    def add_src_repos(self, source_repos):
        """adds a list of source repos to the apt repo

        :param list source_repos: repos to add to sources list
        """
        for source_repo in source_repos:
            lgr.debug('Adding source repository {0}'.format(source_repo))
            if os.path.splitext(source_repo)[1] == '.rpm':
                sh.rpm('-ivh', source_repo, _ok_code=[0, 1])
            else:
                self.download(source_repo, dir='/etc/yum.repos.d/')

    def add_key(self, key_file):
        """adds a list of keys to the local repo

        :param string key_files: key files paths
        """
        lgr.debug('Adding key {0}'.format(key_file))
        # can't do import=key_file as import is unusable as an argument
        sh.rpm('--import', key_file)
