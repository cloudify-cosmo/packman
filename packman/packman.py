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
# TODO: (READ) review https://speakerdeck.com/schisamo/eat-the-whole-bowl-building-a-full-stack-installer-with-omnibus  # NOQA
# TODO: (IMPRV) redo RepoHandler implementation with generic one. should pull all repo handling commands from config  # NOQA
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
import exceptions as exc

import definitions as defs

import os
import fabric.api as fab
import sys
import platform
import urllib2

# __all__ = ['list']

SUPPORTED_DISTROS = ('Ubuntu', 'debian', 'centos')
DEFAULT_COMPONENTS_FILE = 'packages.py'
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


def _import_components_dict(components_file):
    """returns a components file dictionary

    :param string components_file: components_file to search in
    :rtype: `dict` with components configuration
    """
    # get components file path
    components_file = components_file or os.path.join(
        os.getcwd(), DEFAULT_COMPONENTS_FILE)
    lgr.debug('components file is: {0}'.format(components_file))
    # append to path for importing
    sys.path.append(os.path.dirname(components_file))
    try:
        return __import__(os.path.basename(os.path.splitext(
            components_file)[0])).PACKAGES
    except ImportError:
        lgr.error('could not import packages.py file. please verify that '
                  'it exists in the specified path')
        # TODO: (IMPRV) add conditional raising with verbosity dependency
        # TODO: (IMPRV) throughout the code
        # if int(lgr.getEffectiveLevel()) > DEFAULT_BASE_LOGGING_LEVEL:
        raise exc.PackagerError('missing components file')
        # sys.exit(1)


def get_component_config(component_name, components_dict=None,
                         components_file=None):
    """returns a component's configuration

    if `components_dict` is not supplied, a packages.py file in the cwd will be
    assumed unless `components_file` is explicitly given.
    after a `components_dict` is defined, a `component_config` will be returned
    for the specified component_name.

    :param string component: component name to retrieve config for.
    :param dict components_dict: dict containing components configuration
    :param string components_file: components file to search in
    :rtype: `dict` representing component configuration
    """
    if components_dict is None:
        components_dict = {}
    lgr.debug('retrieving configuration for {0}'.format(component_name))
    try:
        if not components_dict:
            components_dict = _import_components_dict(components_file)
        lgr.debug('{0} config retrieved successfully'.format(component_name))
        return components_dict[component_name]
    except KeyError:
        lgr.error('package configuration for'
                  ' {0} was not found, terminating...'.format(component_name))
        raise exc.PackagerError('no config found for package')


def packman_runner(action='pack', components_file=None, components=None,
                   excluded=None, verbose=False):
    """logic for running packman. mainly called from the cli (pkm.py)

    if no `components_file` is supplied, we will assume a local packages.py
    as `components_file`.

    if `components` are supplied, they will be iterated over.
    if `excluded` are supplied, they will be ignored.

    if a pack.py or get.py files are present, and an action_component
    function exists in the files, those functions will be used.
    else, the base get and pack methods supplied with packman will be used.
    so for instance, if you have a component named `x`, and you want to write
    your own `get` function for it. Just write a get_x() function in get.py.

    :param string action: action to perform (get, pack)
    :param string components_file: path to file containing component config
    :param string components: comma delimited list of components to perform
     `action` on.
    :param string excluded: comma delimited list of components to exclude
    :param bool verbose: determines output verbosity level
    :rtype: `None`
    """
    def _build_excluded_components_list(excluded_components):
        lgr.debug('building excluded components list...')
        return filter(None, (excluded_components or "").split(','))

    def _build_components_list(components, xcom_list, components_dict):
        lgr.debug('building components list...')
        com_list = []
        if components:
            for component in components.split(','):
                com_list.append(component)
            # and raise if same component appears in both lists
            if set(com_list) & set(xcom_list):
                lgr.error('your components list and excluded components '
                          'list contain a similar item.')
                raise exc.PackagerError('components list and excluded list '
                                        'are conflicting')
        # else iterate over all components in components file
        else:
            for component, values in components_dict.items():
                com_list.append(component)
            # and rewrite the list after removing excluded components
            for xcom in xcom_list:
                com_list = [com for com in com_list if com != xcom]
        return com_list

    def _import_overriding_methods(action):
        lgr.debug('importing overriding methods file...')
        return __import__(os.path.basename(os.path.splitext(
            os.path.join(os.getcwd(), '{0}.py'.format(action)))[0]))

    utils.set_global_verbosity_level(verbose)
    # import dict of all components
    components_dict = _import_components_dict(components_file)
    # append excluded components to list.
    xcom_list = _build_excluded_components_list(excluded)
    lgr.debug('excluded components list: {0}'.format(xcom_list))
    # append components to list if a list is supplied
    com_list = _build_components_list(components, xcom_list, components_dict)
    lgr.debug('components list: {0}'.format(com_list))
    # if at least 1 component exists
    if com_list:
        # iterate and run action
        for component in com_list:
            # looks for the overriding methods file in the current path
            if os.path.isfile(os.path.join(os.getcwd(), '{0}.py'.format(
                    action))):
                # imports the overriding methods file
                # TODO: allow sending parameters to the overriding methods
                overr_methods = _import_overriding_methods(action)
                # replace hyphens with underscores and remove dots from the
                # overriding methods names
                # also, convert to lowercase to correspond with overriding
                # method names.
                component_re = component.replace('-', '_')
                component_re = component_re.replace('.', '')
                component_re = component_re.lower()
                # if the method was found in the overriding file, run it.
                if hasattr(overr_methods, '{0}_{1}'.format(
                        action, component_re)):
                    getattr(
                        overr_methods, '{0}_{1}'.format(
                            action, component_re))()
                # else run the default action method
                else:
                    # TODO: check for bad action
                    globals()[action](get_component_config(
                        component, components_file=components_file))
            # else run the default action method
            else:
                globals()[action](get_component_config(
                    component, components_file=components_file))
    else:
        raise exc.PackagerError('no components to handle,'
                                ' check your components file')


def get(component):
    """retrieves resources for packaging

    .. note:: component params are defined in packages.py

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
    # you can send the component dict directly, or retrieve it from
    # the packages.py file by sending its name
    c = component if type(component) is dict \
        else get_component_config(component)

    # define params for packaging
    source_urls = c.get(defs.PARAM_SOURCE_URLS, [])
    source_repos = c.get(defs.PARAM_SOURCE_REPOS, [])
    source_ppas = c.get(defs.PARAM_SOURCE_PPAS, [])
    source_keys = c.get(defs.PARAM_SOURCE_KEYS, [])
    reqs = c.get(defs.PARAM_REQS, [])
    prereqs = c.get(defs.PARAM_PREREQS, [])
    modules = c.get(defs.PARAM_MODULES, [])
    gems = c.get(defs.PARAM_GEMS, [])
    sources_path = c.get(defs.PARAM_SOURCES_PATH, False)
    overwrite = c.get(defs.PARAM_OVERWRITE_SOURCES, True)

    common = utils.Handler()
    if centos:
        repo = yum.Handler()
    elif debian:
        repo = apt.Handler()
    retr = retrieve.Handler()
    py = python.Handler()
    rb = ruby.Handler()

    # should the source dir be removed before retrieving package contents?
    if overwrite:
        lgr.info('overwrite enabled. removing {0} before retrieval'.format(
            sources_path))
        common.rmdir(sources_path)
    else:
        if common.is_dir(sources_path):
            lgr.error('the destination directory for this package already '
                      'exists and overwrite is disabled.')
    # create the directories required for package creation...
    if not common.is_dir(sources_path):
        common.mkdir(sources_path)

    # TODO: (TEST) raise on "command not supported by distro"
    # TODO: (FEAT) add support for building packages from source
    repo.install(prereqs)
    # if there's a source repo to add... add it.
    repo.add_src_repos(source_repos)
    # if there's a source ppa to add... add it?
    if source_ppas:
        if not debian:
            raise exc.PackagerError('ppas not supported by {0}'.format(
                get_distro()))
        repo.add_ppa_repos(source_ppas)
    # get a key for the repo if it's required..
    retr.download(source_keys, dir=sources_path)
    for key in source_keys:
        key_file = urllib2.unquote(key).decode('utf8').split('/')[-1]
        repo.add_key(os.path.join(sources_path, key_file))
    # retrieve the source for the package
    for source_url in source_urls:
        # retrieve url file extension
        url_ext = os.path.splitext(source_url)[1]
        # if the source file is an rpm or deb, we want to download
        # it to the archives folder. yes, it's a dreadful solution...
        if url_ext in ('.rpm', '.deb'):
            lgr.debug('the file is a {0} file. we\'ll download it '
                      'to the archives folder'.format(url_ext))
            # elif file:
            #     path, name = os.path.split(file)
            #     file = path + '/archives/' + file
            retr.download(source_url, dir=os.path.join(
                sources_path, 'archives'))
        else:
            retr.download(source_url, dir=sources_path)
    # download any other requirements if they exist
    repo.download(reqs, sources_path)
    # download relevant python modules...
    py.get_modules(modules, sources_path)
    # download relevant ruby gems...
    rb.get_gems(gems, sources_path)
    lgr.info('package retrieval completed successfully!')


def pack(component):
    """creates a package according to the provided package configuration
    in packages.py
    uses fpm (https://github.com/jordansissel/fpm/wiki) to create packages.

    .. note:: component params are defined in packages.py but can be passed
     directly to the pack function as a dict.

    .. note:: param names in packages.py can be overriden by editing
     definitions.py which also has an explanation on each param.

    :param string|dict component: string or dict representing component
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
    :param bool mock: indicates whether a mock pack will be created
     (for testing purposes. does not use fpm)
    :rtype: `None`
    """

    # get the cwd since fpm will later change it.
    cwd = os.getcwd()
    # you can send the component dict directly, or retrieve it from
    # the packages.py file by sending its name
    c = component if type(component) is dict \
        else get_component_config(component)

    # define params for packaging process
    name = c.get(defs.PARAM_NAME)
    version = c.get(defs.PARAM_VERSION, False)
    bootstrap_template = c.get(defs.PARAM_BOOTSTRAP_TEMPLATE_PATH, False)
    bootstrap_script = c.get(defs.PARAM_BOOTSTRAP_SCRIPT_PATH, False)
    bootstrap_script_in_pkg = os.path.join(
        cwd, c[defs.PARAM_BOOTSTRAP_SCRIPT_IN_PACKAGE_PATH]) \
        if defs.PARAM_BOOTSTRAP_SCRIPT_IN_PACKAGE_PATH in c else False
    src_pkg_type = c.get(defs.PARAM_SOURCE_PACKAGE_TYPE, False)
    dst_pkg_types = c.get(defs.PARAM_DESTINATION_PACKAGE_TYPES, [])
    if not dst_pkg_types:
        lgr.debug('destination package type ommitted')
        if centos:
            lgr.debug('assuming default type: {0}'.format(
                PACKAGE_TYPES['centos']))
            dst_pkg_types = [PACKAGE_TYPES['centos']]
        elif debian:
            lgr.debug('assuming default type: {0}'.format(
                PACKAGE_TYPES['debian']))
            dst_pkg_types = [PACKAGE_TYPES['debian']]
    sources_path = c.get(defs.PARAM_SOURCES_PATH, False)
    # TODO: (STPD) JEEZ... this archives thing is dumb...
    # TODO: (STPD) replace it with a normal destination path
    tmp_pkg_path = '{0}/archives'.format(c[defs.PARAM_SOURCES_PATH]) \
        if defs.PARAM_SOURCES_PATH else False
    package_path = c.get(defs.PARAM_PACKAGE_PATH, False)
    depends = c.get(defs.PARAM_DEPENDS, False)
    config_templates = c.get(defs.PARAM_CONFIG_TEMPLATE_CONFIG, False)
    overwrite = c.get(defs.PARAM_OVERWRITE_OUTPUT_PACKAGE, True)
    keep_sources = c.get(defs.PARAM_KEEP_SOURCES, True)

    common = utils.Handler()
    templates = templater.Handler()

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
    lgr.info('packing up component: {0}'.format(name))
    # this checks if a package needs to be created. If no source package type
    # is supplied, the assumption is that packages are only being downloaded
    # so if there's a source package type...
    if src_pkg_type:
        # if the source dir for the package exists
        if common.is_dir(sources_path):
            # change the path to the destination path, since fpm doesn't
            # accept (for now) a dst dir, but rather creates the package in
            # the cwd.
            with fab.lcd(tmp_pkg_path):
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
                        tmp_pkg_path, dst_pkg_type), package_path)
        else:
            lgr.error('sources dir {0} does\'nt exist, termintating...'
                      .format(sources_path))
            # maybe bluntly exit since this is all irrelevant??
            raise exc.PackagerError('sources dir missing')
    else:
        lgr.info("isolating archives...")
        for dst_pkg_type in dst_pkg_types:
            common.mv('{0}/*.{1}'.format(
                tmp_pkg_path, dst_pkg_type), package_path)
    lgr.info('package creation completed successfully!')
    if not keep_sources:
        lgr.debug('removing sources...')
        common.rmdir(sources_path)


def main():
    lgr.debug('running in main...')

if __name__ == '__main__':
    main()

centos = get_distro() in ('centos')
debian = get_distro() in ('Ubuntu', 'debian')
