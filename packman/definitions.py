# flake8: NOQA

# packman base definitions
PACKAGER_TEMPLATE_PATH = "package-templates/"  # directory which contains config for all modules

# packman base params
PARAM_NAME = 'name'  # a mandatory 'string' representing the package's name
PARAM_VERSION = 'version'  # a mandatory 'string' representing the package's version
PARAM_DEPENDS = 'depends'  # an optional [list] of the dependencies of the package
PARAM_REQUIRES = 'requires'  # an optional [list] of the requirements to download
PARAM_PACKAGE_PATH = 'package_path'  # a mandatory 'string' representing the destination path to be used in the packaging process
PARAM_SOURCES_PATH = 'sources_path'  # a mandatory 'string' representing the source path to which files will be downloaded
PARAM_SOURCE_PACKAGE_TYPE = 'source_package_type'  # an optional 'string' representing the source type of the package (as supported by fpm)
PARAM_DESTINATION_PACKAGE_TYPES = 'destination_package_types'  # a mandatory [list] representing the destination types of the packages you'd like to create (as supported by fpm)
PARAM_BOOTSTRAP_SCRIPT_PATH = 'bootstrap_script'  # an optional 'string' representing a path to which the bootstrap script (generated from the template) will be written
PARAM_BOOTSTRAP_TEMPLATE_PATH = 'bootstrap_template'  # an optional 'string' representing a bootstrap script path to be appended to a deb or rpm (appended)
PARAM_OVERWRITE_OUTPUT = 'overwrite_package'  # an optional bool representing whether to overwrite a destination package by default
PARAM_OVERWRITE_SOURCES = 'overwrite_sources'  # an optional bool representing whether to overwrite sources when retrieving package sources
PARAM_CONFIG_TEMPLATE_CONFIG = 'config_templates'  # an optional {dict} of config files and templates
PARAM_PYTHON_MODULES = 'python_modules'  # an optional [list] of python modules to install into a virtualenv
PARAM_RUBY_GEMS = 'ruby_gems'  # an optional [list] of ruby gems to download
PARAM_VIRTUALENV = 'virtualenv'  # an optional {dict} containing a venv path and a [list] of modules to install
PARAM_NODE_PACKAGES = 'node_packages'  # an optional [list] of node packages to download
PARAM_SOURCE_URLS = 'source_urls'  # an optional 'string' representing the sources to download # TOOD: REPLACE WIT [LIST]!
PARAM_SOURCE_REPOS = 'source_repos'  # an optional 'string' representing repos to add to the repos list
PARAM_SOURCE_PPAS = 'source_ppas'  # an optional 'string' representing a ppa repository to add
PARAM_SOURCE_KEYS = 'source_keys'  # an optional 'string' representing a key to download
PARAM_REQS = 'requires'  # an optional [list] of requirements to download from the local distributions repos
PARAM_PREREQS = 'prereqs'  # an optional [list] of prerequirements to install from before retrieving the sources or packgaging
PARAM_KEEP_SOURCES = 'keep_sources'  # an optional 'bool' representing whether to keep the retrieved sources after packaging

# packman configuration files generation params
PARAM_CONFIG_TEMPLATE_DIR = 'template_dir'  # an optional 'dict' containing config for generating config files from a templates directory
# if PARAM_CONFIG_TEPMLATE_DIR is used:
PARAM_CONFIG_TEMPALTES_DIR_TEMPLATES_PATH = 'templates'  # a mandatory 'string' stating where the template files reside
PARAM_CONFIG_TEMPALTES_DIR_CONFIG_DIR = 'config_dir'  # a mandatory 'string' stating where to in the package dir the processed files should reside.

PARAM_CONFIG_TEMPLATE_FILE = 'template_file'  # an optional 'dict' containing config  for generating a config file from a template file
# if PARAM_CONFIG_TEMPLATE_FILE is used:
PARAM_CONFIG_TEMPALTES_FILE_TEMPLATE_FILE = 'template'  # a mandatory 'string' stating where the specific template file resides
PARAM_CONFIG_TEMPALTES_FILE_OUTPUT_FILE = 'output_file'  # a mandatory 'string' stating the name of the output config file.
PARAM_CONFIG_TEMPALTES_FILE_CONFIG_DIR = 'config_dir'  # a mandatory 'string' stating where to in the package dir the processed file should reside.

PARAM_CONFIG_CONFIG_DIR = 'config_dir'  # an optional 'dict' containing config for copying config files from a config files directory
# if PARAM_CONFIG_CONFIG_DIR is used:
PARAM_CONFIG_FILES_CONFIGS_PATH = 'files'  # a mandatory 'string' stating where the origin config files reside.
PARAM_CONFIG_FILES_CONFIGS_DIR = 'config_dir'  # a mandatory 'string' stating where to in the package dir the processed file should reside.

PARAM_CONFIG_CONFIG_FILE = 'config_file'  # an optional 'dict' containing config from copying a config file from a directory. (NOT IMPLEMENTED)
