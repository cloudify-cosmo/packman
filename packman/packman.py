#!/usr/bin/env python
# #
# ###### Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

# TODO: (FEAT) add http://megastep.org/makeself/ support
# TODO: (FEAT) add http://semver.org/ support
# TODO: (FEAT) add support to download and run from github repos so that "components" repos can be created  # NOQA

import logger
import utils

import python
import yum
import retrieve
import apt
import ruby
import templater
import fpm
import codes

import definitions as defs

import os
import yaml
import fabric.api as fab
import sys
import platform

# __all__ = ['list']

SUPPORTED_DISTROS = ('Ubuntu', 'debian', 'centos')
DEFAULT_PACKAGES_FILE = 'packages.yaml'
PACKAGE_TYPES = {
    "centos": "rpm",
    "debian": "deb",
}


lgr = logger.init()


def get_distro():
    """returns the machine's distro
    """
    return platform.dist()[0]


def check_distro(supported=SUPPORTED_DISTROS, verbose=False):
    """checks that the machine's distro is supported

    :param tuple supported: tuple of supported distros
    :param bool verbose: verbosity level
    """
    utils.set_global_verbosity_level(verbose)
    distro = get_distro()
    lgr.debug('Distribution Identified: {0}'.format(distro))
    if distro not in supported:
        lgr.error('Your distribution is not supported.'
                  'Supported Disributions are:')
        for distro in supported:
            lgr.error('    {0}'.format(distro))
        raise RuntimeError('distro not supported')


def _import_packages_dict(config_file=None):
    """returns a configuration object

    :param string config_file: path to config file
    """
    if config_file is None:
        try:
            with open(DEFAULT_PACKAGES_FILE, 'r') as c:
                return yaml.safe_load(c.read())['packages']
        except:
            lgr.error('No config file defines and could not find '
                      'packages.yaml in currect directory.')
            sys.exit(codes.mapping['packages_file_not_found'])
    # get config file path
    lgr.debug('config file is: {}'.format(config_file))
    # append to path for importing
    try:
        lgr.info('importing config...')
        with open(config_file, 'r') as c:
            return yaml.safe_load(c.read())['packages']
    except IOError as ex:
        lgr.error(ex.message)
        lgr.error('Cannot access config file')
        sys.exit(codes.mapping['cannot_access_config_file'])
    except (yaml.parser.ParserError, yaml.scanner.ScannerError) as ex:
        lgr.error(ex.message)
        lgr.error('Invalid yaml file')
        sys.exit(codes.mapping['invalid_yaml_file'])


def get_package_config(package_name, packages_dict=None,
                       packages_file=None):
    """returns a package's configuration

    if `packages_dict` is not supplied, a packages.py file in the cwd will be
    assumed unless `packages_file` is explicitly given.
    after a `packages_dict` is defined, a `package_config` will be returned
    for the specified package_name.

    :param string package: package name to retrieve config for.
    :param dict packages_dict: dict containing packages configuration
    :param string packages_file: packages file to search in
    :rtype: `dict` representing package configuration
    """
    if packages_dict is None:
        packages_dict = {}
    lgr.debug('retrieving configuration for {0}'.format(package_name))
    try:
        if not packages_dict:
            packages_dict = _import_packages_dict(packages_file)
        lgr.debug('{0} config retrieved successfully'.format(package_name))
        return packages_dict[package_name]
    except KeyError:
        lgr.error('package configuration for'
                  ' {0} was not found, terminating...'.format(package_name))
        sys.exit(codes.mapping['no_config_found_for_package'])


def packman_runner(action, packages_file=None, packages=None,
                   excluded=None, verbose=False):
    """logic for running packman. mainly called from the cli (pkm.py)

    if no `packages_file` is supplied, we will assume a local packages.py
    as `packages_file`.

    if `packages` are supplied, they will be iterated over.
    if `excluded` are supplied, they will be ignored.

    if a pack.py or get.py files are present, and an action_package
    function exists in the files, those functions will be used.
    else, the base get and pack methods supplied with packman will be used.
    so for instance, if you have a package named `x`, and you want to write
    your own `get` function for it. Just write a get_x() function in get.py.

    :param string action: action to perform (get, pack)
    :param string packages_file: path to file containing package config
    :param string packages: comma delimited list of packages to perform
     `action` on.
    :param string excluded: comma delimited list of packages to exclude
    :param bool verbose: determines output verbosity level
    :rtype: `None`
    """
    def _build_excluded_packages_list(excluded_packages):
        lgr.debug('building excluded packages list...')
        return filter(None, (excluded_packages or "").split(','))

    def _build_packages_list(packages, xcom_list, packages_dict):
        lgr.debug('building packages list...')
        com_list = []
        if packages:
            for package in packages.split(','):
                com_list.append(package)
            # and raise if same package appears in both lists
            if set(com_list) & set(xcom_list):
                lgr.error('your packages list and excluded packages '
                          'list contain a similar item.')
                sys.exit(codes.mapping['excluded_conflict'])
        # else iterate over all packages in packages file
        else:
            for package, values in packages_dict.items():
                com_list.append(package)
            # and rewrite the list after removing excluded packages
            for xcom in xcom_list:
                com_list = [com for com in com_list if com != xcom]
        return com_list

    def _import_overriding_methods(action):
        lgr.debug('importing overriding methods file...')
        return __import__(os.path.basename(os.path.splitext(
            os.path.join(os.getcwd(), '{0}.py'.format(action)))[0]))

    def _rename_package(package):
        # replace hyphens with underscores and remove dots from the
        # overriding methods names
        # also, convert to lowercase to correspond with overriding
        # method names.
        package_re = package.replace('-', '_')
        package_re = package_re.replace('.', '')
        package_re = package_re.lower()
        return package_re

    utils.set_global_verbosity_level(verbose)
    # import dict of all packages
    packages_dict = _import_packages_dict(packages_file)
    # append excluded packages to list.
    xcom_list = _build_excluded_packages_list(excluded)
    lgr.debug('excluded packages list: {0}'.format(xcom_list))
    # append packages to list if a list is supplied
    com_list = _build_packages_list(packages, xcom_list, packages_dict)
    lgr.debug('packages list: {0}'.format(com_list))
    # if at least 1 package exists
    if com_list:
        # iterate and run action
        for package in com_list:
            # looks for the overriding methods file in the current path
            if os.path.isfile(os.path.join(
                    os.getcwd(), '{0}.py'.format(action))):
                # imports the overriding methods file
                # TODO: allow sending parameters to the overriding methods
                overr_methods = _import_overriding_methods(action)
                # rename overriding package name by convention
                package = _rename_package(package)
                # if the method was found in the overriding file, run it.
                if hasattr(overr_methods, '{0}_{1}'.format(action, package)):
                    getattr(overr_methods, '{0}_{1}'.format(action, package))()
                # else run the default action method
                else:
                    # TODO: check for bad action
                    globals()[action](get_package_config(
                        package, packages_file=packages_file))
            # else run the default action method
            else:
                globals()[action](get_package_config(
                    package, packages_file=packages_file))
    else:
        lgr.error('no packages to handle, check your packages file')
        sys.exit(codes.mapping['no_packages_defined'])


def get(package):
    """retrieves resources for packaging

    .. note:: package params are defined in packages.py

    .. note:: param names in packages.py can be overriden by editing
     definitions.py which also has an explanation on each param.

    :param dict package: dict representing package config
     as configured in packages.py
     will be appended to the filename and to the package
     depending on its type
    :param string version: version to append to package
    :param list source_urls: source urls to download
    :param list source_repos: source repos to add for package retrieval
    :param list source_ppas: source ppas to add for package retrieval
    :param list source_keys: source keys to download
    :param list reqs: list of apt requirements
    :param string sources_path: path where downloaded source are placed
    :param list modules: list of python modules to download
    :param list gems: list of ruby gems to download
    :param bool overwrite: indicated whether the sources directory be
     erased before creating a new package
    :rtype: `None`
    """

    def handle_sources_path(sources_path, overwrite):
        # should the source dir be removed before retrieving package contents?
        u = utils.Handler()
        if overwrite:
            lgr.info('overwrite enabled. removing {0} before retrieval'.format(
                sources_path))
            u.rmdir(sources_path)
        else:
            if u.is_dir(sources_path):
                lgr.error('the destination directory for this package already '
                          'exists and overwrite is disabled.')
                sys.exit(codes.mapping['path_already_exists_no_overwrite'])
        # create the directories required for package creation...
        if not u.is_dir(sources_path):
            u.mkdir(sources_path)

    # you can send the package dict directly, or retrieve it from
    # the packages.py file by sending its name
    c = package if isinstance(package, dict) \
        else get_package_config(package)

    # set handlers
    repo = yum.Handler() if CENTOS else apt.Handler() if DEBIAN else None
    retr = retrieve.Handler()
    py = python.Handler()
    rb = ruby.Handler()

    # everything will be downloaded here
    sources_path = c.get(defs.PARAM_SOURCES_PATH, False)
    handle_sources_path(
        sources_path, c.get(defs.PARAM_OVERWRITE_SOURCES, True))

    # TODO: (TEST) raise on "command not supported by distro"
    # TODO: (FEAT) add support for building packages from source
    repo.install(c.get(defs.PARAM_PREREQS, []))
    repo.add_src_repos(c.get(defs.PARAM_SOURCE_REPOS, []))
    repo.add_ppa_repos(c.get(defs.PARAM_SOURCE_PPAS, []), DEBIAN, get_distro())
    retr.downloads(c.get(defs.PARAM_SOURCE_KEYS, []), sources_path)
    repo.add_keys(c.get(defs.PARAM_SOURCE_KEYS, []), sources_path)
    retr.downloads(c.get(defs.PARAM_SOURCE_URLS, []), sources_path)
    repo.download(c.get(defs.PARAM_REQS, []), sources_path)
    py.get_modules(c.get(defs.PARAM_MODULES, []), sources_path)
    rb.get_gems(c.get(defs.PARAM_GEMS, []), sources_path)
    lgr.info('package retrieval completed successfully!')


def pack(package):
    """creates a package according to the provided package configuration
    in packages.py
    uses fpm (https://github.com/jordansissel/fpm/wiki) to create packages.

    .. note:: package params are defined in packages.py but can be passed
     directly to the pack function as a dict.

    .. note:: param names in packages.py can be overriden by editing
     definitions.py which also has an explanation on each param.

    :param string|dict package: string or dict representing package
     name or params (coorespondingly) as configured in packages.py
    :param string name: package's name
     will be appended to the filename and to the package
     depending on its type
    :param string version: version to append to package
    :param string src_pkg_type: package source type (as supported by fpm)
    :param list dst_pkg_types: package destination types (as supported by fpm)
    :param string src_path: path containing sources
     from which package will be created
    :param string tmp_pkg_path: path where temp package is placed
    :param string package_path: path where final package is placed
    :param string bootstrap_script: path to place generated script
    :param string bootstrap_script_in_pkg:
    :param dict config_templates: configuration dict for the package's
     config files
    :param bool overwrite: indicates whether the destination directory be
     erased before creating a new package
    :param bool keep_sources: indicates whether the sources will be deleted
     after the packaging process is done
    :rtype: `None`
    """

    def handle_package_path(package_path, sources_path, tmp_pkg_path, name,
                            overwrite):
        if not common.is_dir(os.path.join(package_path, 'archives')):
            common.mkdir(os.path.join(package_path, 'archives'))
        # can't use sources_path == tmp_pkg_path for the package... duh!
        if sources_path == tmp_pkg_path:
            lgr.error('source and destination paths must'
                      ' be different to avoid conflicts!')
        if overwrite:
            lgr.info('overwrite enabled. removing {0}/{1}* before packaging'
                     .format(package_path, name))
            common.rm('{0}/{1}*'.format(package_path, name))
        # TODO: (CHK) why did I do this?
        if src_pkg_type:
            common.rmdir(tmp_pkg_path)
            common.mkdir(tmp_pkg_path)

    def set_dst_pkg_type():
        lgr.debug('destination package type ommitted')
        if CENTOS:
            lgr.debug('assuming default type: {0}'.format(
                PACKAGE_TYPES['centos']))
            return [PACKAGE_TYPES['centos']]
        elif DEBIAN:
            lgr.debug('assuming default type: {0}'.format(
                PACKAGE_TYPES['debian']))
            return [PACKAGE_TYPES['debian']]

    # get the cwd since fpm will later change it.
    cwd = os.getcwd()
    # you can send the package dict directly, or retrieve it from
    # the packages.py file by sending its name
    c = package if type(package) is dict \
        else get_package_config(package)

    # define params for packaging process
    name = c.get(defs.PARAM_NAME)
    version = c.get(defs.PARAM_VERSION, False)
    bootstrap_template = c.get(defs.PARAM_BOOTSTRAP_TEMPLATE_PATH, False)
    bootstrap_script = c.get(defs.PARAM_BOOTSTRAP_SCRIPT_PATH, False)
    bootstrap_script_in_pkg = os.path.join(
        cwd, c[defs.PARAM_BOOTSTRAP_SCRIPT_IN_PACKAGE_PATH]) \
        if defs.PARAM_BOOTSTRAP_SCRIPT_IN_PACKAGE_PATH in c else False
    src_pkg_type = c.get(defs.PARAM_SOURCE_PACKAGE_TYPE, False)
    dst_pkg_types = c.get(
        defs.PARAM_DESTINATION_PACKAGE_TYPES, set_dst_pkg_type())
    sources_path = c.get(defs.PARAM_SOURCES_PATH, False)
    # TODO: (STPD) JEEZ... this archives thing is dumb...
    # TODO: (STPD) replace it with a normal destination path
    # tmp_pkg_path = '{0}/archives'.format(c[defs.PARAM_SOURCES_PATH]) \
    #     if defs.PARAM_SOURCES_PATH else False
    # tmp_pkg_path = c.get(defs.PARAM_PACKAGE_PATH, '.')
    package_path = c.get(defs.PARAM_PACKAGE_PATH, False)
    depends = c.get(defs.PARAM_DEPENDS, False)
    config_templates = c.get(defs.PARAM_CONFIG_TEMPLATE_CONFIG, False)
    overwrite = c.get(defs.PARAM_OVERWRITE_OUTPUT_PACKAGE, True)
    keep_sources = c.get(defs.PARAM_KEEP_SOURCES, True)

    common = utils.Handler()
    templates = templater.Handler()

    # handle_package_path(
    #     package_path, sources_path, tmp_pkg_path, name, overwrite)

    lgr.info('generating package scripts and config files...')
    if config_templates:
        templates.generate_configs(c)
    if bootstrap_script or bootstrap_script_in_pkg:
        if bootstrap_template and bootstrap_script:
            templates.generate_from_template(
                c, bootstrap_script, bootstrap_template)
        if bootstrap_template and bootstrap_script_in_pkg:
            templates.generate_from_template(
                c, bootstrap_script_in_pkg, bootstrap_template)
            lgr.debug('granting execution permissions')
            utils.do('chmod +x {0}'.format(bootstrap_script_in_pkg))
            lgr.debug('copying bootstrap script to package directory')
            common.cp(bootstrap_script_in_pkg, sources_path)
    lgr.info('packing up package: {0}'.format(name))
    # this checks if a package needs to be created. If no source package type
    # is supplied, the assumption is that packages are only being downloaded
    # so if there's a source package type...
    if src_pkg_type:
        if not os.listdir(sources_path) == []:
            # change the path to the destination path, since fpm doesn't
            # accept (for now) a dst dir, but rather creates the package in
            # the cwd.
            with fab.lcd(package_path):
                for dst_pkg_type in dst_pkg_types:
                    i = fpm.Handler(name, src_pkg_type, dst_pkg_type,
                                    sources_path, sudo=True)
                    i.execute(version=version, force=overwrite,
                              depends=depends, after_install=bootstrap_script,
                              chdir=False, before_install=None)
                    if dst_pkg_type == "tar.gz":
                        lgr.debug('converting tar to tar.gz...')
                        utils.do('sudo gzip {0}.tar*'.format(name))
                    lgr.info("isolating archives...")
                    common.mv('{0}/*.{1}'.format(
                        package_path, dst_pkg_type), package_path)
        else:
            lgr.error('Sources directory is empty. '
                      'There\'s nothing to package.')
            sys.exit(codes.mapping['sources_empty'])
    else:
        lgr.info("isolating archives...")
        for dst_pkg_type in dst_pkg_types:
            common.mv('{0}/*.{1}'.format(
                package_path, dst_pkg_type), package_path)
    lgr.info('package creation completed successfully!')
    if not keep_sources:
        lgr.debug('removing sources...')
        common.rmdir(sources_path)


def main():
    lgr.debug('running in main...')

if __name__ == '__main__':
    main()

CENTOS = get_distro() in ('centos')
DEBIAN = get_distro() in ('Ubuntu', 'debian')
