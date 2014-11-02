import os

import utils
import definitions as defs
import logger
import exceptions as exc
import jinja2 as jinja


lgr = logger.init()


class Handler(utils.Handler):

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
        output_path = '{0}/{1}/{2}'.format(
            component[defs.PARAM_SOURCES_PATH], config_dir, output_file)
        # create the directory to put the config in after it's
        # genserated
        self.mkdir('{0}/{1}'.format(
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
                output_path = '{0}/{1}/{2}'.format(
                    component[defs.PARAM_SOURCES_PATH], config_dir,
                    output_file)

                self.mkdir('{0}/{1}'.format(
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
        self.mkdir('{0}/{1}'.format(
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
            raise exc.PackagerError('component must be of type dict')
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
            raise exc.PackagerError('template_dir must be of type string')
        if self.is_dir(template_dir):
            env = jinja.Environment(loader=jinja.FileSystemLoader(
                template_dir))
        else:
            lgr.error('template dir missing')
            raise exc.PackagerError('template dir missing')
        if type(template_file) is not str:
            raise exc.PackagerError('template_file must be of type string')
        if self.is_file(os.path.join(template_dir, template_file)):
            template = env.get_template(template_file)
        else:
            lgr.error('template file missing')
            raise exc.PackagerError('template file missing')

        try:
            lgr.debug('generating template from {0}/{1}'.format(
                      template_dir, template_file))
            return template.render(var_dict)
        except Exception as e:
            lgr.error('could not generate template ({0})'.format(e))
            raise exc.PackagerError('could not generate template')

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
            raise exc.PackagerError('could not write to file {0}'.format(
                output_path))
