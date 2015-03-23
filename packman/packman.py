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
# import importlib

import definitions as defs

import sh
import os
import yaml
import sys

SUPPORTED_DISTROS = ('Ubuntu', 'debian', 'centos')
DEFAULT_PACKAGES_FILE = 'packages.yaml'
PACKAGE_TYPES = {"centos": "rpm", "debian": "deb"}
SUPPORTED_PACKAGE_TYPES = ['deb', 'rpm', 'tar', 'zip', 'tar.gz']


lgr = logger.init()


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
    lgr.debug('Config file is: {0}'.format(config_file))
    # append to path for importing
    try:
        lgr.info('Importing config...')
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

    if `packages_dict` is not supplied, a packages.yaml file in the cwd will be
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
    lgr.debug('Retrieving configuration for {0}'.format(package_name))
    try:
        if not packages_dict:
            packages_dict = _import_packages_dict(packages_file)
        lgr.debug('{0} config retrieved successfully'.format(package_name))
        return packages_dict[package_name]
    except KeyError:
        lgr.error('Package configuration for'
                  ' {0} was not found, terminating...'.format(package_name))
        sys.exit(codes.mapping['no_config_found_for_package'])


def packman_runner(action, packages_file=None, packages=None,
                   excluded=None, verbose=False):
    """logic for running packman. mainly called from the cli (pkm.py)

    if no `packages_file` is supplied, we will assume a local packages.yaml
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
    def build_excluded_packages_list(excluded_packages):
        lgr.debug('Building excluded packages list...')
        return filter(None, (excluded_packages or "").split(','))

    def build_packages_list(packages, xcluded_packages_list, packages_dict):
        lgr.debug('Building packages list...')
        package_list = []
        # if you specified a list of packages
        if packages:
            package_list = [p for p in packages.split(',')]
            # raise if same package appears in both lists
            if set(package_list) & set(xcluded_packages_list):
                lgr.error('Your packages list and excluded packages '
                          'list contain a similar item.')
                sys.exit(codes.mapping['excluded_conflict'])
        # else iterate over all packages in packages file
        else:
            package_list = [p for p in packages_dict.keys()]
            # and rewrite the list after removing excluded packages
            for xcld in xcluded_packages_list:
                package_list = [pkg for pkg in package_list if pkg != xcld]
        return package_list

    def import_overriding_methods(action):
        lgr.debug('Importing overriding methods file...')
        sys.path.append(os.getcwd())
        return __import__(action)

    def rename_package(package):
        # this is meant to unify package names so that common
        # dashes, hyphens, dots and case errors do not occur.
        package_re = package.replace('-', '_')
        package_re = package_re.replace('.', '')
        package_re = package_re.lower()
        return package_re

    utils.set_global_verbosity_level(verbose)
    packages_dict = _import_packages_dict(packages_file)
    xcluded_packages_list = build_excluded_packages_list(excluded)
    lgr.debug('Excluded packages list: {0}'.format(xcluded_packages_list))
    # append packages to list if a list is supplied
    package_list = build_packages_list(
        packages, xcluded_packages_list, packages_dict)
    lgr.debug('Package list: {0}'.format(package_list))
    # if at least 1 package exists
    if package_list:
        for package in package_list:
            package_dict = get_package_config(
                package_name=package,
                packages_dict=packages_dict,
                packages_file=packages_file)
            validate = Validate(package_dict)
            validate.validate_package_properties()
            # looks for the overriding methods file in the current path
            if os.path.isfile(os.path.join(
                    os.getcwd(), '{0}.py'.format(action))):
                # TODO: allow sending parameters to the overriding methods
                overr_methods = import_overriding_methods(action)
                package = rename_package(package)
                # if the method was found in the overriding file, run it.
                if hasattr(overr_methods, '{0}_{1}'.format(action, package)):
                    getattr(overr_methods, '{0}_{1}'.format(action, package))()
                # else run the default action method
                else:
                    # TODO: check for bad action
                    globals()[action](package_dict)
            else:
                globals()[action](package_dict)
    else:
        lgr.error('No packages to handle, Verify that your packages file '
                  'contains packages and that you did not exclude '
                  'all of them.')
        sys.exit(codes.mapping['no_packages_defined'])


def get(package):
    """retrieves resources for packaging

    .. note:: package params are defined in packages.yaml

    .. note:: param names in packages.yaml can be overriden by editing
     definitions.py which also has an explanation on each param.

    :param dict package: dict representing package config
     as configured in packages.yaml
     will be appended to the filename and to the package
     depending on its type
    :rtype: `None`
    """

    def handle_sources_path(sources_path, overwrite):
        if sources_path is None:
            lgr.error('Sources path key is required under {0} '
                      'in packages.yaml.'.format(defs.PARAM_SOURCES_PATH))
            sys.exit(codes.mapping['sources_path_required'])
        u = utils.Handler()
        # should the source dir be removed before retrieving package contents?
        if overwrite:
            lgr.info('Overwrite enabled. removing {0} before retrieval'.format(
                sources_path))
            u.rmdir(sources_path)
        else:
            if os.path.isdir(sources_path):
                lgr.error('The destination directory for this package already '
                          'exists and overwrite is disabled.')
                sys.exit(codes.mapping['path_already_exists_no_overwrite'])
        # create the directories required for package creation...
        if not os.path.isdir(sources_path):
            u.mkdir(sources_path)

    # you can send the package dict directly, or retrieve it from
    # the packages.yaml file by sending its name
    c = package if isinstance(package, dict) else get_package_config(package)

    repo = yum.Handler() if CENTOS else apt.Handler() if DEBIAN else None
    retr = retrieve.Handler()
    py = python.Handler()
    rb = ruby.Handler()

    sources_path = c.get(defs.PARAM_SOURCES_PATH, None)
    handle_sources_path(
        sources_path, c.get(defs.PARAM_OVERWRITE_SOURCES, True))

    # TODO: (TEST) raise on "command not supported by distro"
    # TODO: (FEAT) add support for building packages from source
    repo.install(c.get(defs.PARAM_PREREQS, []))
    repo.add_src_repos(c.get(defs.PARAM_SOURCE_REPOS, []))
    if c.get(defs.PARAM_SOURCE_PPAS, []) and not DEBIAN:
        lgr.error('ppas not supported by {0}'.format(utils.get_distro()))
        sys.exit(codes.mapping['ppa_not_supported_by_distro'])
    repo.add_ppa_repos(c.get(defs.PARAM_SOURCE_PPAS, []))
    retr.downloads(c.get(defs.PARAM_SOURCE_KEYS, []), sources_path)
    repo.add_keys(c.get(defs.PARAM_SOURCE_KEYS, []), sources_path)
    retr.downloads(c.get(defs.PARAM_SOURCE_URLS, []), sources_path)
    repo.download(c.get(defs.PARAM_REQS, []), sources_path)
    if c.get(defs.PARAM_VIRTUALENV):
        with utils.chdir(os.path.abspath(sources_path)):
            py.make_venv(c['virtualenv']['path'])
        py.install(c['virtualenv']['modules'], c['virtualenv']['path'],
                   sources_path)
    py.get_modules(c.get(defs.PARAM_PYTHON_MODULES, []), sources_path)
    rb.get_gems(c.get(defs.PARAM_RUBY_GEMS, []), sources_path)
    # nd.get_packages(c.get(defs.PARAM_NODE_PACKAGES, []), sources_path)
    lgr.info('Package retrieval completed successfully!')


def pack(package):
    """creates a package according to the provided package configuration
    in packages.yaml
    uses fpm (https://github.com/jordansissel/fpm/wiki) to create packages.

    .. note:: package params are defined in packages.yaml but can be passed
     directly to the pack function as a dict.

    .. note:: param names in packages.yaml can be overriden by editing
     definitions.py which also has an explanation on each param.

    :param string|dict package: string or dict representing package
     name or params (coorespondingly) as configured in packages.yaml
    :rtype: `None`
    """

    def handle_package_path(package_path, sources_path, name, overwrite):
        if not os.path.isdir(package_path):
            u.mkdir(package_path)
        if sources_path == package_path:
            lgr.error('Sources path and package paths must'
                      ' be different to avoid conflicts!')
            sys.exit(codes.mapping['sources_and_package_paths_identical'])
        if overwrite:
            lgr.info('Overwrite enabled. Removing {0}/{1}* '
                     'before packaging'.format(package_path, name))
            u.rm('{0}/{1}*'.format(package_path, name))

    def set_dst_pkg_type():
        lgr.debug('Destination package type omitted')
        if CENTOS:
            lgr.debug('Assuming default type: {0}'.format(
                PACKAGE_TYPES['centos']))
            return [PACKAGE_TYPES['centos']]
        elif DEBIAN:
            lgr.debug('Assuming default type: {0}'.format(
                PACKAGE_TYPES['debian']))
            return [PACKAGE_TYPES['debian']]

    def convert_tar_to_targz(tar_file):
        lgr.debug('Converting tar to tar.gz...')
        sh.gzip(tar_file)

    # you can send the package dict directly, or retrieve it from
    # the packages.yaml file by sending its name
    c = package if isinstance(package, dict) else get_package_config(package)

    name = c.get(defs.PARAM_NAME)
    bootstrap_template = c.get(defs.PARAM_BOOTSTRAP_TEMPLATE_PATH, False)
    bootstrap_script = c.get(defs.PARAM_BOOTSTRAP_SCRIPT_PATH, False)
    src_pkg_type = c.get(defs.PARAM_SOURCE_PACKAGE_TYPE, False)
    dst_pkg_types = c.get(
        defs.PARAM_DESTINATION_PACKAGE_TYPES, set_dst_pkg_type())
    try:
        sources_path = os.path.abspath(c[defs.PARAM_SOURCES_PATH])
    except KeyError:
        lgr.error('Sources path key is required under {0} '
                  'in packages.yaml.'.format(defs.PARAM_SOURCES_PATH))
    package_path = c.get(defs.PARAM_PACKAGE_PATH, os.getcwd())

    u = utils.Handler()
    templates = templater.Handler()

    handle_package_path(
        package_path, sources_path, name,
        c.get(defs.PARAM_OVERWRITE_OUTPUT, False))

    lgr.info('Generating package scripts and config files...')
    if c.get(defs.PARAM_CONFIG_TEMPLATE_CONFIG, False):
        templates.generate_configs(c)
    if bootstrap_script:
        if bootstrap_template:
            templates.generate_from_template(
                c, bootstrap_script, bootstrap_template)
        for package in dst_pkg_types:
            # when creating a deb or rpm, it isn't required to chmod the script
            if package in ('tar', 'tar.gz'):
                lgr.debug('Granting execution permissions to script.')
                sh.chmod('+x', bootstrap_script)
                lgr.debug('Copying bootstrap script to package directory')
                u.cp(bootstrap_script, sources_path)

    lgr.info('Packaging: {0}'.format(name))
    # this checks if a package needs to be created. If no source package type
    # is supplied, the assumption is that packages are only being downloaded
    # so if there's a source package type...
    if not os.listdir(sources_path) == []:
        fpm_params = {
            'version': c.get(defs.PARAM_VERSION, False),
            'force': c.get(defs.PARAM_OVERWRITE_OUTPUT, True),
            'depends': c.get(defs.PARAM_DEPENDS, False),
            'after_install': False if not bootstrap_script
            else os.path.abspath(bootstrap_script),
            'chdir': False,
            'before_install': None
        }
        # change the path to the destination path, since fpm doesn't
        # accept (for now) a dst dir, but rather creates the package in
        # the cwd.
        with utils.chdir(os.path.abspath(package_path)):
            for dst_pkg_type in dst_pkg_types:
                packager = fpm.Handler(
                    name, src_pkg_type, dst_pkg_type, sources_path)
                result = packager.execute(**fpm_params)
                if not result:
                    lgr.error('Failed to create package.')
                    sys.exit(codes.mapping['failed_create_package'])
            if dst_pkg_type == "tar.gz":
                tar_file = '{0}.tar'.format(name)
                targz_file = tar_file + '.gz'
                if os.path.isfile(targz_file):
                    if c.get(defs.PARAM_OVERWRITE_OUTPUT):
                        u.rm(targz_file)
                    else:
                        lgr.error('{0} already exists and overwrite '
                                  'is false.'.format(targz_file))
                        sys.exit(codes.mapping['targz_exists'])
                convert_tar_to_targz(tar_file)
    else:
        lgr.error('Sources directory is empty. Nothing to package.')
        sys.exit(codes.mapping['sources_empty'])
    lgr.info('Package creation completed successfully!')

    if not c.get(defs.PARAM_KEEP_SOURCES, True):
        lgr.debug('Removing sources...')
        u.rmdir(sources_path)


class Validate():

    def __init__(self, package):
        self.package = package

    def validate_package_properties(self):
        if defs.PARAM_DESTINATION_PACKAGE_TYPES in self.package:
            self.destination_package_types(
                self.package[defs.PARAM_DESTINATION_PACKAGE_TYPES])

    def destination_package_types(self, package_types):
        if not isinstance(package_types, list):
            lgr.error('{0} key must be of type "list".'.format(
                defs.PARAM_DESTINATION_PACKAGE_TYPES))
            sys.exit(codes.mapping['package_types_must_be_list'])
        for package_type in package_types:
            if package_type not in SUPPORTED_PACKAGE_TYPES:
                lgr.error('{0} key must contain one of: {1}.'.format(
                    defs.PARAM_DESTINATION_PACKAGE_TYPES,
                    SUPPORTED_PACKAGE_TYPES))
                sys.exit(codes.mapping['unsupported_package_type'])


def main():
    lgr.debug('Running in main...')

if __name__ == '__main__':
    main()

# TODO: fail on Windows
CENTOS = utils.get_distro() in ('centos')
DEBIAN = utils.get_distro() in ('Ubuntu', 'debian')
