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

import logging
import logging.config

import packman_config as pkm_conf
import definitions as defs

import os
from fabric.api import *  # NOQA
import sys
import re
from time import sleep
from jinja2 import Environment, FileSystemLoader
from platform import dist
import urllib2
import glob

# __all__ = ['list']

SUPPORTED_DISTROS = ('Ubuntu', 'debian', 'centos')
DEFAULT_COMPONENTS_FILE = 'packages.py'
PACKAGE_TYPES = {
    "centos": "rpm",
    "debian": "deb",
}
DEFAULT_BASE_LOGGING_LEVEL = logging.INFO
DEFAULT_VERBOSE_LOGGING_LEVEL = logging.DEBUG


def init_logger(base_level=DEFAULT_BASE_LOGGING_LEVEL,
                verbose_level=DEFAULT_VERBOSE_LOGGING_LEVEL,
                logging_config=None):
    """initializes a base logger

    you can use this to init a logger in any of your files.
    this will use config.py's LOGGER param and logging.dictConfig to configure
    the logger for you.

    :param int|logging.LEVEL base_level: desired base logging level
    :param int|logging.LEVEL verbose_level: desired verbose logging level
    :param dict logging_dict: dictConfig based configuration.
     used to override the default configuration from config.py
    :rtype: `python logger`
    """
    if logging_config is None:
        logging_config = {}
    logging_config = logging_config or pkm_conf.LOGGER
    # TODO: (IMPRV) only perform file related actions if file handler is
    # TODO: (IMPRV) defined.

    log_dir = os.path.expanduser(
        os.path.dirname(
            pkm_conf.LOGGER['handlers']['file']['filename']))
    if os.path.isfile(log_dir):
        sys.exit('file {0} exists - log directory cannot be created '
                 'there. please remove the file and try again.'
                 .format(log_dir))
    try:
        logfile = pkm_conf.LOGGER['handlers']['file']['filename']
        d = os.path.dirname(logfile)
        if not os.path.exists(d) and not len(d) == 0:
            os.makedirs(d)
        logging.config.dictConfig(logging_config)
        lgr = logging.getLogger('user')
        # lgr.setLevel(base_level) if not pkm_conf.VERBOSE \
        lgr.setLevel(base_level)
        return lgr
    except ValueError as e:
        sys.exit('could not initialize logger.'
                 ' verify your logger config'
                 ' and permissions to write to {0} ({1})'
                 .format(logfile, e))

lgr = init_logger()


def set_global_verbosity_level(is_verbose_output=False):
    """sets the global verbosity level for console and the lgr logger.

    :param bool is_verbose_output: should be output be verbose
    """
    global verbose_output
    verbose_output = is_verbose_output
    if verbose_output:
        lgr.setLevel(logging.DEBUG)
    else:
        lgr.setLevel(logging.INFO)
    # print 'level is: ' + str(lgr.getEffectiveLevel())


def get_distro():
    """returns the machine's distro
    """
    return dist()[0]


def check_distro(supported=SUPPORTED_DISTROS, verbose=False):
    """checks that the machine's distro is supported

    :param tuple supported: tuple of supported distros
    :param bool verbose: verbosity level
    """
    set_global_verbosity_level(verbose)
    distro = get_distro()
    lgr.debug('Distribution Identified: {}'.format(distro))
    if distro not in supported:
        lgr.error('Your distribution is not supported.'
                  'Supported Disributions are:')
        for distro in supported:
            lgr.error('    {}'.format(distro))
        raise RuntimeError('distro not supported')


def import_components_dict(components_file):
    """returns a components dictionary

    :param string components_file: components_file to search in
    :rtype: `dict` with components configuration
    """
    # get components file path
    components_file = components_file or os.path.join(
        os.getcwd(), DEFAULT_COMPONENTS_FILE)
    lgr.debug('components file is: {}'.format(components_file))
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
        raise PackagerError('missing components file')
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
            components_dict = import_components_dict(components_file)
        lgr.debug('{0} config retrieved successfully'.format(component_name))
        return components_dict[component_name]
    except KeyError:
        lgr.error('package configuration for'
                  ' {0} was not found, terminating...'.format(component_name))
        raise PackagerError('no config found for package')


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
    so for instance, if you have a component named `x`

    :param string action: action to perform (get, pack)
    :param string components_file: path to file containing component config
    :param string components: comma delimited list of components to perform
     `action` on.
    :param string excluded: comma delimited list of components to exclude
    :param bool verbose: determines output verbosity level
    :rtype: `None`
    """
    def _build_excluded_components_list(excluded_components):
        return filter(None, (excluded or "").split(','))

    def _build_components_list(components, xcom_list, components_dict):
        com_list = []
        if components:
            for component in components.split(','):
                com_list.append(component)
            # and raise if same component appears in both lists
            if set(com_list) & set(xcom_list):
                lgr.error('your components list and excluded components '
                          'list contain a similar item.')
                raise PackagerError('components list and excluded list '
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
        return __import__(os.path.basename(os.path.splitext(
            os.path.join(os.getcwd(), '{}.py'.format(action)))[0]))

    set_global_verbosity_level(verbose)
    # import dict of all components
    components_dict = import_components_dict(components_file)
    # append excluded components to list.
    xcom_list = _build_excluded_components_list(excluded)
    lgr.debug('excluded components list: {}'.format(xcom_list))
    # append components to list if a list is supplied
    com_list = _build_components_list(components, xcom_list, components_dict)
    lgr.debug('components list: {}'.format(com_list))
    # if at least 1 component exists
    if com_list:
        # iterate and run action
        for component in com_list:
            # looks for the overriding methods file in the current path
            if os.path.isfile(os.path.join(os.getcwd(), '{}.py'.format(
                    action))):
                # imports the overriding methods file
                # TODO: allow sending parameters to the overriding methods
                overr_methods = _import_overriding_methods(action)
                # replace hyphens with underscores and remove dots from the
                # overriding methods names
                component_re = component.replace('-', '_')
                component_re = component_re.replace('.', '')
                # if the method was found in the overriding file, run it.
                if hasattr(overr_methods, '{}_{}'.format(
                        action, component_re)):
                    getattr(
                        overr_methods, '{}_{}'.format(
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
        raise PackagerError('no components to handle,'
                            ' check your components file')


def get(component):
    """retrieves resources for packaging

    .. note:: component params are defined in packages.py

    .. note:: param names in packages.py can be overriden by editing
     definitions.py which also has an explanation on each param.

    :param dict package: dict representing package config
     as configured in packages.py
    :param string name: package's name
     will be appended to the filename and to the package
     depending on its type
    :param string version: version to append to package
    :param string source_url: source url to download
    :param string source_repo: source repo to add for package retrieval
    :param string source_ppa: source ppa to add for package retrieval
    :param string source_key: source key to download
    :param string key_file: key file path
    :param list reqs: list of apt requirements
    :param string dst_path: path where downloaded source are placed
    :param string package_path: path where final package is placed
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
    name = c.get(defs.PARAM_NAME)
    source_repos = c.get(defs.PARAM_SOURCE_REPOS, [])
    source_ppas = c.get(defs.PARAM_SOURCE_PPAS, [])
    source_keys = c.get(defs.PARAM_SOURCE_KEYS, [])
    source_urls = c.get(defs.PARAM_SOURCE_URLS, [])
    key_files = c.get(defs.PARAM_KEY_FILES_PATH, [])
    reqs = c.get(defs.PARAM_REQS, [])
    prereqs = c.get(defs.PARAM_PREREQS, [])
    modules = c.get(defs.PARAM_MODULES, [])
    gems = c.get(defs.PARAM_GEMS, [])
    dst_path = c.get(defs.PARAM_SOURCES_PATH, False)
    overwrite = c.get(defs.PARAM_OVERWRITE_SOURCES, True)

    common = CommonHandler()
    if centos:
        repo_handler = YumHandler()
    elif debian:
        repo_handler = AptHandler()
    dl_handler = WgetHandler()
    py_handler = PythonHandler()
    ruby_handler = RubyHandler()

    # should the source dir be removed before retrieving package contents?
    if overwrite:
        lgr.info('overwrite enabled. removing {0} before retrieval'.format(
            dst_path))
        common.rmdir(dst_path)
    else:
        if common.is_dir(dst_path):
            lgr.error('the destination directory for this package already '
                      'exists and overwrite is disabled.')
    # create the directories required for package creation...
    if not common.is_dir(dst_path):
        common.mkdir(dst_path)

    # TODO: (TEST) raise on "command not supported by distro"
    # TODO: (FEAT) add support for building packages from source
    repo_handler.installs(prereqs)
    # if there's a source repo to add... add it.
    repo_handler.add_src_repos(source_repos)
    # if there's a source ppa to add... add it?
    if source_ppas:
        if not debian:
            raise PackagerError('ppas not supported by {}'.format(
                get_distro()))
        repo_handler.add_ppa_repos(source_ppas)
    # get a key for the repo if it's required..
    dl_handler.downloads(source_keys, dir=dst_path)
    for key in source_keys:
        key_file = urllib2.unquote(key).decode('utf8').split('/')[-1]
        repo_handler.add_key(os.path.join(dst_path, key_file))
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
            dl_handler.download(source_url, dir=os.path.join(
                dst_path, 'archives'))
        else:
            dl_handler.download(source_url, dir=dst_path)
    # add the repo key
    if key_files:
        repo_handler.add_keys(key_files)
        repo_handler.update()
    # download any other requirements if they exist
    for req in reqs:
        if type(req) is dict:
            home = os.path.expanduser('~')
            common.mkdir('{}/tmp'.format(home), sudo=False)
            dl_handler.download(
                req['url'], file='{0}/tmp/{1}_reqs.tar.gz'.format(
                    home, name), sudo=False)
            common.untar('{0}/tmp'.format(home),
                         '{0}/tmp/{1}_reqs.tar.gz'.format(
                             home, name), strip=0, sudo=False)
            cf = glob.glob('{}/tmp/packages.py'.format(home))
            if not cf:
                cf = glob.glob('{}/tmp/**/packages.py'.format(home))
            # cfpath = os.path.splitext(cf[0])[0]
            print 'HAHAAAAAAAAAAAAAAAAAAAA', cf[0]
            cffile = name + '_' + os.path.basename(cf[0])
            cfdir = os.path.dirname(cf[0])
            cfnew = os.path.join(cfdir, cffile)
            os.rename(cf[0], cfnew)
            print 'HAHAAAAAAAAAAAAAAAAAAAA', cfnew
            for component in req['components']:
                c = get_component_config(
                    component, components_file=cfnew)
                # get(c)
                # pack(c)
        else:
            repo_handler.downloads(reqs, dst_path)
    # download relevant python modules...
    py_handler.get_python_modules(modules, dst_path)
    # download relevant ruby gems...
    ruby_handler.get_ruby_gems(gems, dst_path)


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
    :param string dst_pkg_type: package destination type (as supported by fpm)
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

    # define params for packaging
    name = c.get(defs.PARAM_NAME)
    version = c.get(defs.PARAM_VERSION, False)
    bootstrap_template = c.get(defs.PARAM_BOOTSTRAP_TEMPLATE_PATH, False)
    bootstrap_script = c.get(defs.PARAM_BOOTSTRAP_SCRIPT_PATH, False)
    bootstrap_script_in_pkg = os.path.join(
        cwd, c[defs.PARAM_BOOTSTRAP_SCRIPT_IN_PACKAGE_PATH]) \
        if defs.PARAM_BOOTSTRAP_SCRIPT_IN_PACKAGE_PATH in c else False
    src_pkg_type = c.get(defs.PARAM_SOURCE_PACKAGE_TYPE, False)
    dst_pkg_type = c.get(defs.PARAM_DESTINATION_PACKAGE_TYPE, False)
    # identifies pkg type automatically if not specified explicitly
    if not dst_pkg_type:
        lgr.debug('destination package type ommitted')
        if centos:
            lgr.debug('assuming default type: {}'.format(
                PACKAGE_TYPES['centos']))
            dst_pkg_type = PACKAGE_TYPES['centos']
        elif debian:
            lgr.debug('assuming default type: {}'.format(
                PACKAGE_TYPES['debian']))
            dst_pkg_type = PACKAGE_TYPES['debian']
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

    common = CommonHandler()
    tmp_handler = TemplateHandler()

    # if the package_path doesn't exist, create it
    if not common.is_dir(os.path.join(package_path, 'archives')):
        common.mkdir(os.path.join(package_path, 'archives'))
    # can't use sources_path == tmp_pkg_path for the package... duh!
    if sources_path == tmp_pkg_path:
        lgr.error('source and destination paths must'
                  ' be different to avoid conflicts!')
    # should the packaging process overwrite the previous packages?
    if overwrite:
        lgr.info('overwrite enabled. removing {0}/{1}* before packaging'
                 .format(package_path, name))
        common.rm('{0}/{1}*'.format(package_path, name))
    # if the package is ...
    # TODO: (CHK) why did I do this?
    if src_pkg_type:
        common.rmdir(tmp_pkg_path)
        common.mkdir(tmp_pkg_path)

    lgr.info('generating package scripts and config files...')
    # if there are configuration templates to generate configs from...
    if config_templates:
        tmp_handler.generate_configs(c)
    # if bootstrap scripts are required, generate them.
    if bootstrap_script or bootstrap_script_in_pkg:
        # bootstrap_script - bootstrap script to be attached to the package
        if bootstrap_template and bootstrap_script:
            tmp_handler.generate_from_template(c, bootstrap_script,
                                               bootstrap_template)
        # bootstrap_script_in_pkg - same but for putting inside the package
        if bootstrap_template and bootstrap_script_in_pkg:
            tmp_handler.generate_from_template(c, bootstrap_script_in_pkg,
                                               bootstrap_template)
            # if it's in_pkg, grant it exec permissions and copy it to the
            # package's path.
            lgr.debug('granting execution permissions')
            do('chmod +x {0}'.format(bootstrap_script_in_pkg))
            lgr.debug('copying bootstrap script to package directory')
            common.cp(bootstrap_script_in_pkg, sources_path)
    lgr.info('packing up component: {0}'.format(name))
    # if a package needs to be created (not just files copied)...
    if src_pkg_type:
        # if the source dir for the package exists
        if common.is_dir(sources_path):
            # change the path to the destination path, since fpm doesn't
            # accept (for now) a dst dir, but rather creates the package in
            # the cwd.
            with lcd(tmp_pkg_path):
                # these will handle the different packaging cases based on
                # the requirement. for instance, if a bootstrap script
                # exists, and there are dependencies for the package, run
                # fpm with the relevant flags.
                i = fpmHandler(name, src_pkg_type, dst_pkg_type,
                               sources_path, sudo=True)
                i.fpm(version=version, force=overwrite, depends=depends,
                      after_install=bootstrap_script, chdir=False,
                      before_install=None)
                if dst_pkg_type == "tar.gz":
                    do('sudo gzip {0}*'.format(name))
        # apparently, the src for creation the package doesn't exist...
        # what can you do?
        else:
            lgr.error('sources dir {0} does\'nt exist, termintating...'
                      .format(sources_path))
            # maybe bluntly exit since this is all irrelevant??
            raise PackagerError('sources dir missing')

    # make sure the final destination for the package exists..
    if not common.is_dir(package_path):
        common.mkdir(package_path)
    lgr.info("isolating archives...")
    # and then copy the final package over..
    common.cp('{0}/*.{1}'.format(tmp_pkg_path, dst_pkg_type), package_path)
    lgr.info('package creation completed successfully!')
    if not keep_sources:
        common.rmdir(sources_path)


def do(command, attempts=2, sleep_time=3, accepted_err_codes=None,
       capture=False, combine_stderr=False, sudo=False):
    """executes a command locally with retries on failure.

    if a `command` execution is successful, it will return a fabric
    object with the output (x.stdout, x.stderr, x.succeeded, etc..)

    else, it will retry an `attempts` number of attempts and if all fails
    it will return the fabric output object.
    obviously, `attempts` must be larger than 0...

    :param string command: shell command to be executed
    :param int attempts: number of attempts to perform on failure
    :param int sleep_time: sleeptime between attempts
    :param bool capture: should the output be captured for parsing?
    :param bool combine_stderr: combine stdout and stderr (NOT YET IMPL)
    :param bool sudo: run as sudo
    :rtype: `responseObject` (for fabric operation)
    """
    if attempts < 1:
        raise RuntimeError('attempts must be at least 1')
    if not sleep_time > 0:
        raise RuntimeError('sleep_time must be larger than 0')
    if not accepted_err_codes:
        accepted_err_codes = []

    def _execute():
        for execution in xrange(attempts):
            with settings(warn_only=True):
                with hide('warnings'):
                    x = local('sudo {0}'.format(command), capture) if sudo \
                        else local(command, capture)
                if x.succeeded or x.return_code in accepted_err_codes:
                    lgr.debug('successfully executed: ' + command)
                    return x
                lgr.warning('failed to run command: {0} -retrying ({1}/{2})'
                            .format(command, execution + 1, attempts))
                sleep(sleep_time)
        lgr.error('failed to run command: {0} even after {1} attempts'
                  ' with output: {2}'
                  .format(command, execution, x.stdout))
        return x

    with hide('running'):
        return _execute()


class CommonHandler():
    """common class to handle files and directories
    """
    def find_in_dir(self, dir, pattern, sudo=True):
        """
        finds file/s in a dir

        :param string dir: directory to look in
        :param string patten: what to look for
        :rtype: ``stdout`` `string` if found, else `None`
        """
        lgr.debug('looking for {0} in {1}'.format(pattern, dir))
        x = do('find {0} -iname "{1}" -exec echo {{}} \;'
               .format(dir, pattern), capture=True, sudo=sudo)
        return x.stdout if x.succeeded else None

    def is_dir(self, dir):
        """checks if a directory exists

        :param string dir: directory to check
        :rtype: `bool`
        """
        lgr.debug('checking if {0} exists'.format(dir))
        if os.path.isdir(dir):
            lgr.debug('{0} exists'.format(dir))
            return True
        else:
            lgr.debug('{0} does not exist'.format(dir))
            return False

    def is_file(self, file):
        """checks if a file exists

        :param string file: file to check
        :rtype: `bool`
        """
        lgr.debug('checking if {0} exists'.format(file))
        if os.path.isfile(file):
            lgr.debug('{0} exists'.format(file))
            return True
        else:
            lgr.debug('{0} does not exist'.format(file))
            return False

    def touch(self, file, sudo=True):
        """creates a file

        :param string file: file to touch
        """
        lgr.debug('creating file {0}'.format(file))
        return do('touch {0}'.format(file), sudo=sudo)

    def mkdir(self, dir, sudo=True):
        """creates (recursively) a directory

        :param string dir: directory to create
        """
        lgr.debug('creating directory {0}'.format(dir))
        return do('mkdir -p {0}'.format(dir), sudo=sudo) \
            if not os.path.isdir(dir) \
            else lgr.debug('directory already exists, skipping.')
        return False

    def rmdir(self, dir, sudo=True):
        """deletes a directory

        :param string dir: directory to remove
        """
        lgr.debug('attempting to remove directory {0}'.format(dir))
        return do('rm -rf {0}'.format(dir), sudo=sudo) \
            if os.path.isdir(dir) else lgr.debug('dir doesn\'t exist')
        return False

    # TODO: (IMPRV) handle multiple files differently
    def rm(self, file, sudo=True):
        """deletes a file or a set of files

        :param string file(s): file(s) to remove
        """
        lgr.debug('removing files {0}'.format(file))
        return do('rm {0}'.format(file), sudo=sudo) if os.path.isfile(file) \
            else lgr.debug('file(s) do(es)n\'t exist')
        return False

    def cp(self, src, dst, recurse=True, sudo=True):
        """copies (recuresively or not) files or directories

        :param string src: source to copy
        :param string dst: destination to copy to
        :param bool recurse: should the copying process be recursive?
        """
        lgr.debug('copying {0} to {1}'.format(src, dst))
        return do('cp -R {0} {1}'.format(src, dst), sudo=sudo) if recurse \
            else do('cp {0} {1}'.format(src, dst), sudo=sudo)

    def tar(self, chdir, output_file, input_path, opts='zvf', sudo=True):
        """tars an input file or directory

        :param string chdir: change to this dir before archiving
        :param string output_file: tar output file path
        :param string input: input path to create tar from
        :param string opts: tar opts
        """
        lgr.debug('tar-ing {0}'.format(output_file))
        return do('tar -C {0} -c{1} {2} {3}'.format(
            chdir, opts, output_file, input_path), sudo=sudo)

    def untar(self, chdir, input_file, opts='zvf', strip=0, sudo=True):
        """untars a file

        :param string chdir: change to this dir before extracting
        :param string input_file: file to untar
        :param string opts: tar opts
        """
        lgr.debug('untar-ing {0}'.format(input_file))
        return do('tar -C {0} -x{1} {2} --strip={3}'.format(
            chdir, opts, input_file, strip), sudo=sudo)


class fpmHandler(CommonHandler):
    """packaging handler
    """
    def __init__(self, name, input_type, output_type, source, sudo):
        self.sudo = sudo
        self.name = name
        self.output_type = 'tar' if output_type.startswith('tar') \
            else output_type
        self.input_type = input_type
        self.source = source
        self.command = 'fpm -n {0} -s {1} -t {2} '

    def _build_fpm_cmd_string(self, **kwargs):
        self.command = self.command.format(
            self.name, self.input_type, self.output_type)
        if kwargs['version']:
            self.command += '-v {} '.format(kwargs['version'])
        if kwargs['chdir']:
            self.command += '-C {} '.format(kwargs['chdir'])
        if kwargs['after_install']:
            self.command += '--after-install {} '.format(
                os.path.join(os.getcwd(), kwargs['after_install']))
        if kwargs['before_install']:
            self.command += '--before-install {} '.format(
                os.path.join(os.getcwd(), kwargs['before_install']))
        if kwargs['depends']:
            self.command += "-d " + " -d ".join(kwargs['depends'])
            self.command += " "
        if kwargs['force']:
            self.command += '-f '
        # MUST BE LAST
        self.command += self.source
        lgr.debug('fpm cmd is: {}'.format(self.command))

    def fpm(self, **kwargs):
        self._build_fpm_cmd_string(**kwargs)
        do(self.command, sudo=self.sudo)


class PythonHandler(CommonHandler):
    """python operations handler
    """
    def pips(self, modules, venv=False, attempts=5):
        """pip installs a list of modules

        :param list modules: python modules to ``pip install``
        :param string venv: (optional) if ommited, will use system python
         else, will use `venv` (for virtualenvs and such)
        """
        for module in modules:
            self.pip(module, venv, attempts)

    def pip(self, module, venv=False, attempts=5, sudo=True, timeout='45'):
        """pip installs a module

        :param string module: python module to ``pip install``
        :param string venv: (optional) if ommited, will use system python
         else, will use `venv` (for virtualenvs and such)
        """
        lgr.debug('installing module {0}'.format(module))
        return do('{0}/bin/pip --default-timeout={2} install {1}'
                  ' --process-dependency-links'.format(venv, module, timeout),
                  attempts=attempts, sudo=sudo) \
            if venv else do('pip --default-timeout={2} install {1}'
                            ' --process-dependency-links'.format(
                                venv, module, timeout),
                            attempts=attempts, sudo=sudo)

    def get_python_modules(self, modules, dir=False, venv=False):
        """downloads python modules

        :param list modules: python modules to download
        :param string dir: dir to download modules to
        :param string venv: (optional) if ommited, will use system python
         else, will use `dir` (for virtualenvs and such)
        """
        for module in modules:
            self.get_python_module(module, dir, venv)

    def get_python_module(self, module, dir=False, venv=False):
        """downloads a python module

        :param string module: python module to download
        :param string dir: dir to download module to
        :param string venv: (optional) if ommited, will use system python
         else, will use `dir` (for virtualenvs and such)
        """
        lgr.debug('downloading module {0}'.format(module))
        return do('sudo {0}/pip install --no-use-wheel'
                  ' --process-dependency-links --download "{1}/" {2}'
                  .format(venv, dir, module)) \
            if venv else do('sudo pip install --no-use-wheel'
                            ' --process-dependency-links --download "{0}/" {1}'
                            .format(dir, module))

    def check_module_installed(self, name, dir=False):
        """checks to see that a module is installed

        :param string name: module to check for
        :param string dir: (optional) if ommited, will use system python
         else, will use `dir` (for virtualenvs and such)
        """
        lgr.debug('checking whether {0} is installed'.format(name))
        x = do('pip freeze', capture=True) if not dir else \
            do('{0}/pip freeze'.format(dir), capture=True)
        if re.search(r'{0}'.format(name), x.stdout):
            lgr.debug('module {0} is installed'.format(name))
            return True
        else:
            lgr.debug('module {0} is not installed'.format(name))
            return False

    # TODO: (FEAT) support virtualenv --relocate OR
    # TODO: (FEAT) support whack http://mike.zwobble.org/2013/09/relocatable-python-virtualenvs-using-whack/ # NOQA
    def venv(self, venv_dir, sudo=True):
        """creates a virtualenv

        :param string venv_dir: venv path to create
        """
        lgr.debug('creating virtualenv in {0}'.format(venv_dir))
        # if self.check_module_installed('virtualenv'):
        return do('virtualenv {0}'.format(venv_dir), sudo=sudo)
        # else:
        #     lgr.error('virtualenv is not installed. terminating')
        #     raise PackagerError('h0!')


class RubyHandler(CommonHandler):
    def get_ruby_gems(self, gems, dir=False):
        """downloads a list of ruby gems

        :param list gems: gems to download
        :param string dir: directory to download gems to
        """
        for gem in gems:
            self.get_ruby_gem(gem, dir)

    def get_ruby_gem(self, gem, rbenv=False, dir=False):
        """downloads a ruby gem

        :param string gem: gem to download
        :param string dir: directory to download gem to
        """
        lgr.debug('downloading gem {0}'.format(gem))
        # TODO: (TEST) add support for ruby in different environments
        return do('sudo {0}/bin/gem install --no-ri --no-rdoc'
                  ' --install-dir {1} {2}'.format(rbenv, dir, gem)) \
            if rbenv else do('sudo gem install --no-ri --no-rdoc'
                             ' --install-dir {1} {2}'.format(dir, gem))


class YumHandler(CommonHandler):
    @staticmethod
    def update():
        """runs yum update
        """
        lgr.debug('updating local yum repo')
        return do('sudo yum update')

    def check_if_package_is_installed(self, package):
        """checks if a package is installed

        :param string package: package name to check
        :rtype: `bool` representing whether package is installed or not
        """

        lgr.debug('checking if {0} is installed'.format(package))
        x = do('sudo rpm -qa | grep {0}'.format(
            package), attempts=1, accepted_err_codes=[1])
        if x.succeeded:
            lgr.debug('{0} is installed'.format(package))
            return True
        else:
            lgr.error('{0} is not installed'.format(package))
            return False

    def downloads(self, reqs, sources_path):
        """downloads component requirements

        :param list reqs: list of requirements to download
        :param sources_path: path to download requirements to
        """
        for req in reqs:
            self.download(req, sources_path)

    def download(self, package, dir, enable_repo=False):
        """uses yum to download package debs from ubuntu's repo

        :param string package: package to download
        :param string dir: dir to download to
        """
        # TODO: (TEST) run yum reinstall instead of yum install.
        lgr.debug('downloading {0} to {1}'.format(package, dir))
        # TODO: (FIX) yum download exits with an error even if the download
        # TODO: (FIX) succeeded due to a non-zero error message.
        # TODO: (FEAT) add yum enable-repo option
        # TODO: (IMPRV) $(repoquery --requires --recursive --resolve pkg)
        # TODO: (IMPRV) can be used to download deps. test to see if it works.
        if self.check_if_package_is_installed(package):
            return do('sudo yum -y reinstall --downloadonly '
                      '--downloaddir={1}/archives {0}'.format(
                          package, dir), accepted_err_codes=[1])
        else:
            return do('sudo yum -y install --downloadonly '
                      '--downloaddir={1}/archives {0}'.format(
                          package, dir), accepted_err_codes=[1])

    def installs(self, packages):
        """yum installs a list of packages

        :param list package: packages to install
        """
        for package in packages:
            self.install(package)

    def install(self, package):
        """yum installs a package

        :param string package: package to install
        """
        lgr.debug('installing {0}'.format(package))
        do('sudo yum -y install {0}'.format(package))

    def add_src_repos(self, source_repos):
        """adds a list of source repos to the apt repo

        :param list source_repos: repos to add to sources list
        """
        for source_repo in source_repos:
            self.add_src_repo(source_repo)

    def add_src_repo(self, source_repo):
        """adds a source repo to the apt repo

        :param string source_repo: repo to add to sources list
        """
        lgr.debug('adding source repository {0}'.format(source_repo))
        if os.path.splitext(source_repo)[1] == '.rpm':
            return do('sudo rpm -ivh {0}'.format(
                source_repo), accepted_err_codes=[1])
        else:
            dl = WgetHandler()
            dl.download(source_repo, dir='/etc/yum.repos.d/')

    def add_keys(self, key_files):
        """adds a list of keys to the local repo

        :param string key_files: key files paths
        """
        for key_file in key_files:
            self.add_key(key_file)

    def add_key(self, key_file):
        """adds a key to the local repo

        :param string key_file: key file path
        """
        lgr.debug('adding key {0}'.format(key_file))
        return do('sudo rpm --import {0}'.format(key_file))


class AptHandler(CommonHandler):
    def dpkg_name(self, dir):
        """renames deb files to conventional names

        :param string dir: dir to review
        """

        lgr.debug('renaming deb files...')
        return do('dpkg-name {0}/*.deb'.format(dir))

    def check_if_package_is_installed(self, package):
        """checks if a package is installed

        :param string package: package name to check
        :rtype: `bool` representing whether package is installed or not
        """

        lgr.debug('checking if {0} is installed'.format(package))
        x = do('sudo dpkg -s {0}'.format(package), attempts=1)
        if x.succeeded:
            lgr.debug('{0} is installed'.format(package))
            return True
        else:
            lgr.error('{0} is not installed'.format(package))
            return False

    def downloads(self, reqs, sources_path):
        """downloads component requirements

        :param list reqs: list of requirements to download
        :param sources_path: path to download requirements to
        """
        for req in reqs:
            self.download(req, sources_path)

    def download(self, package, dir):
        """uses apt to download package debs from ubuntu's repo

        :param string package: package to download
        :param string dir: dir to download to
        """
        # TODO: (TEST) add an is-package-installed check. if it is
        # TODO: (TEST) run apt-get install --reinstall instead of apt-get
        # TODO: (TEST) install.
        # TODO: (IMPRV) try http://askubuntu.com/questions/219828/getting-deb-package-dependencies-for-an-offline-ubuntu-computer-through-windows  # NOQA
        # TODO: (IMPRV) for downloading requirements
        lgr.debug('downloading {0} to {1}'.format(package, dir))
        # if self.check_if_package_is_installed(package):
        return do('sudo apt-get -y install {0} -d -o=dir::cache={1}'
                  .format(package, dir))
        # else:
        #     return do('sudo apt-get -y install --reinstall '
        #               '{0} -d -o=dir::cache={1}'.format(pkg, dir))

    def autoremove(self, pkg):
        """autoremoves package dependencies

        :param string pkg: package to remove
        """
        lgr.debug('removing unnecessary dependencies...')
        return do('sudo apt-get -y autoremove {0}'.format(pkg))

    def add_src_repos(self, source_repos):
        """adds a list of source repos to the apt repo

        :param list source_repos: repos to add to sources list
        """
        for source_repo in source_repos:
            self.add_src_repo(source_repo)

    def add_src_repo(self, source_repo):
        """adds a source repo to the apt repo

        :param string source_repo: repo to add to sources list
        """
        lgr.debug('adding source repository {0}'.format(source_repo))
        return do('sudo sed -i "2i {0}" /etc/apt/sources.list'
                  .format(source_repo))

    def add_ppa_repos(self, source_ppas):
        """adds a list of ppa repos to the apt repo

        :param list source_ppas: ppa urls to add
        """
        for source_ppa in source_ppas:
            self.add_ppa_repo(source_ppa)

    def add_ppa_repo(self, source_ppa):
        """adds a ppa repo to the apt repo

        :param string source_ppa: ppa url to add
        """
        lgr.debug('adding ppa repository {0}'.format(source_ppa))
        return do('add-apt-repository -y {0}'.format(source_ppa))

    def add_keys(self, key_files):
        """adds a list of keys to the local repo

        :param string key_files: key files paths
        """
        for key_file in key_files:
            self.add_key(key_file)

    def add_key(self, key_file):
        """adds a key to the local repo

        :param string key_file: key file path
        """
        lgr.debug('adding key {0}'.format(key_file))
        return do('sudo apt-key add {0}'.format(key_file))

    @staticmethod
    def update():
        """runs apt-get update
        """
        lgr.debug('updating local apt repo')
        return do('sudo apt-get update')

    def installs(self, packages):
        """apt-get installs a list of packages

        :param list packages: packages to install
        """
        for package in packages:
            self.install(package)

    def install(self, package):
        """apt-get installs a package

        :param string package: package to install
        """
        lgr.debug('installing {0}'.format(package))
        do('sudo apt-get -y install {0}'.format(package))

    def purges(self, packages):
        """completely purges a list of packages from the local repo

        :param list packages: packages name to purge
        """
        for package in packages:
            self.purge(package)

    def purge(self, package):
        """completely purges a package from the local repo

        :param string package: package name to purge
        """
        lgr.debug('attemping to purge {0}'.format(package))
        return do('sudo apt-get -y purge {0}'.format(package))


class WgetHandler(CommonHandler):
    def downloads(self, urls, dir=False, sudo=True):
        """wgets a list of urls to a destination directory

        :param list urls: a list of urls to download
        :param string dir: download to dir...
        """
        for url in urls:
            self.download(url, dir, sudo=sudo)

    def download(self, url, dir=False, file=False, sudo=True):
        """wgets a url to a destination directory or file

        :param string url: url to wget?
        :param string dir: download to dir....
        :param string file: download to file...
        """
        options = '--timeout=30'
        # workaround for archives folder
        if (file and dir) or (not file and not dir):
            lgr.warning('please specify either a directory'
                        ' or file to download to.')
            raise PackagerError('please specify either a directory'
                                ' or file to download to.')
        lgr.debug('downloading {0} to {1}'.format(url, file or dir))
        return do('wget {0} {1} -O {2}'.format(
            url, options, file), sudo=sudo) \
            if file else do('wget {0} {1} -P {2}'
                            .format(url, options, dir), sudo=sudo)


class TemplateHandler(CommonHandler):

    def generate_configs(self, component, sudo=True):
        """generates configuration files from templates

        for every key in the configuration templates sub-dict, if a key
        corresponds with a templates/configs key (as defined in definitions.py)
        the relevant method for creating configuration files will be applied.

        :param dict component: contains the params to use in the template
        """
        # iterate over the config_templates dict in the package's config
        for key, value in \
                component[defs.PARAM_CONFIG_TEMPLATE_CONFIG].items():
            # we'll make some assumptions regarding the structure of the config
            # placement. spliting and joining to make up the positions.

            # and find something to mark that you should generate a template
            # from a file
            if key.startswith(defs.PARAM_CONFIG_TEMPLATE_FILE):
                self._generate_config_from_file(component, value, sudo=sudo)
            # or generate templates from a dir, where the difference
            # would be that the name of the output files will correspond
            # to the names of the template files (removing .template)
            elif key.startswith(defs.PARAM_CONFIG_TEMPLATE_DIR):
                self._generate_configs_from_dir(component, value, sudo=sudo)
            # or just copy static config files...
            elif key.startswith(defs.PARAM_CONFIG_CONFIG_DIR):
                self._generate_static_configs_from_dir(
                    component, value, sudo=sudo)
            else:
                # you can define arbitrary keys in the config_templates
                # dict.. for your bidding,
                # which can then be used as param references.
                pass

    def _generate_config_from_file(self, component, config_params, sudo=True):
        """generates a configuration file from a template file

        if the config directory for the component doesn't exist, it will be
        created after which the config file will be generated into that dir.

        :param string component: component name
        :param dict config_params: file config params
        """
        # where should config reside within the package?
        config_dir = \
            config_params[defs.PARAM_CONFIG_TEMPALTES_FILE_CONFIG_DIR]
        # where is the template dir?
        template_dir = '/'.join(
            config_params[defs.PARAM_CONFIG_TEMPALTES_FILE_TEMPLATE_FILE]
            .split('/')[:-1])
        # where is the template file?
        template_file = \
            config_params[defs.PARAM_CONFIG_TEMPALTES_FILE_TEMPLATE_FILE] \
            .split('/')[-1]
        # the output file's name is...
        output_file = \
            config_params[defs.PARAM_CONFIG_TEMPALTES_FILE_OUTPUT_FILE] \
            if defs.PARAM_CONFIG_TEMPALTES_FILE_OUTPUT_FILE in config_params \
            else '.'.join(template_file.split('.')[:-1])
        # and its path is...
        output_path = '{}/{}/{}'.format(
            component[defs.PARAM_SOURCES_PATH], config_dir, output_file)
        # create the directory to put the config in after it's
        # genserated
        self.mkdir('{}/{}'.format(
            component[defs.PARAM_SOURCES_PATH], config_dir), sudo=sudo)
        # and then generate the config file. WOOHOO!
        self.generate_from_template(component,
                                    output_path,
                                    template_file,
                                    template_dir)

    def _generate_configs_from_dir(self, component, config_params, sudo=True):
        """generates configuration files from a a templates directory

        if the config directory for the `component` doesn't exist, it will be
        created after which the config files will be generated into that dir.

        the source directory, as configured in `config_params` will be iterated
        over and all files will be processed.

        :param string component: component name
        :param dict config_params: file config params
        """
        config_dir = config_params[defs.PARAM_CONFIG_TEMPALTES_DIR_CONFIG_DIR]
        template_dir = \
            config_params[defs.PARAM_CONFIG_TEMPALTES_DIR_TEMPLATES_PATH]
        # iterate over the files in the dir...
        # and just perform the same steps as in _generate_config_from_file
        for subdir, dirs, files in os.walk(template_dir):
            for file in files:
                template_file = file
                output_file = '.'.join(template_file.split('.')[:-1])
                output_path = '{}/{}/{}'.format(
                    component[defs.PARAM_SOURCES_PATH], config_dir,
                    output_file)

                self.mkdir('{}/{}'.format(
                    component[defs.PARAM_SOURCES_PATH], config_dir), sudo=sudo)
                self.generate_from_template(component,
                                            output_path,
                                            template_file,
                                            template_dir)

    def _generate_static_configs_from_dir(self, component, config_params,
                                          sudo=True):
        """copies configuration files from a a configuration files directory

        if the config directory for the `component` doesn't exist, it will be
        created after which the config files will be generated into that dir.

        the source directory, as configured in `config_params` will be iterated
        over and all files will be copied.

        :param string component: component name
        :param dict config_params: file config params
        """
        config_dir = config_params[defs.PARAM_CONFIG_FILES_CONFIGS_DIR]
        files_dir = config_params[defs.PARAM_CONFIG_FILES_CONFIGS_PATH]
        self.mkdir('{}/{}'.format(
            component[defs.PARAM_SOURCES_PATH], config_dir), sudo=sudo)
        # copy the static files to the destination config dir.
        # yep, simple as that...
        self.cp(os.path.join(files_dir, '*'),
                os.path.join(component[defs.PARAM_SOURCES_PATH], config_dir),
                sudo=sudo)

    def generate_from_template(self, component_config, output_file,
                               template_file,
                               templates=defs.PACKAGER_TEMPLATE_PATH):
        """generates configuration files from templates using jinja2
        http://jinja.pocoo.org/docs/

        :param dict component_config: contains the params to use
         in the template
        :param string output_file: output file path
        :param string template_file: template file name
        :param string templates: template files directory
        """
        lgr.debug('generating config file...')
        if type(component_config) is not dict:
            lgr.error('component must be of type dict')
            raise PackagerError('component must be of type dict')
        formatted_text = self._template_formatter(
            templates, template_file, component_config)
        self._make_file(output_file, formatted_text)

    def _template_formatter(self, template_dir, template_file, var_dict):
        """receives a template and returns a formatted version of it
        according to a provided variable dictionary

        :param string template_dir: where all temlate files reside
        :param string template_file: template file name
        :param dict var_dict: dict of all params to be used
         when creating the file
        :rtype: generated template content
        """
        if type(template_dir) is not str:
            raise PackagerError('template_dir must be of type string')
        if self.is_dir(template_dir):
            env = Environment(loader=FileSystemLoader(template_dir))
        else:
            lgr.error('template dir missing')
            raise PackagerError('template dir missing')
        if type(template_file) is not str:
            raise PackagerError('template_file must be of type string')
        if self.is_file(os.path.join(template_dir, template_file)):
            template = env.get_template(template_file)
        else:
            lgr.error('template file missing')
            raise PackagerError('template file missing')

        try:
            lgr.debug('generating template from {0}/{1}'.format(
                      template_dir, template_file))
            return template.render(var_dict)
        except Exception as e:
            lgr.error('could not generate template ({0})'.format(e))
            raise PackagerError('could not generate template')

    def _make_file(self, output_path, content):
        """creates a file from content

        :param string output_path: path to output the generated
         file to
        :param content: content to write to file
        """
        lgr.debug('creating file: {0} with content: \n{1}'.format(
                  output_path, content))
        try:
            with open(output_path, 'w+') as f:
                f.write(content)
        except IOError:
            lgr.error('could not write to file')
            raise PackagerError('could not write to file {0}'
                                .format(output_path))


class PackagerError(Exception):
    pass


def main():
    lgr.debug('running in main...')

if __name__ == '__main__':
    main()

centos = get_distro() in ('centos')
debian = get_distro() in ('Ubuntu', 'debian')
