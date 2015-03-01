########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
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

import packman.exceptions as exc
import packman.logger as logger
import packman.packman as packman
import packman.python as py
import packman.retrieve as retr
import packman.utils as utils
import packman.templater as templater
import packman.codes as codes

import sys
import sh
import testtools
import os
from functools import wraps
from testfixtures import log_capture
import logging
from platform import dist


TEST_DIR = '{0}/test_dir'.format(os.path.expanduser("~"))
TEST_FILE_NAME = 'test_file'
TEST_FILE = TEST_DIR + '/' + TEST_FILE_NAME
TEST_TAR_NAME = 'test_tar.tar.gz'
TEST_TAR = TEST_DIR + '/' + TEST_TAR_NAME
TEST_VENV = '{0}/test_venv'.format(os.path.expanduser("~"))
TEST_MODULE = 'xmltodict'
TEST_MISSING_MODULE = 'mockmodule'
TEST_TEMPLATES_DIR = 'packman/tests/templates'
TEST_TEMPLATE_FILE = 'mock_template.template'
TEST_DL_FILE = 'https://github.com/cloudify-cosmo/packman/archive/master.zip'
TEST_DL_DEB = 'http://ftp.us.debian.org/debian/pool/main/w/wget-el/wget-el_0.5.0-8_all.deb'  # NOQA
TEST_PACKAGES_FILE = 'packman/tests/resources/packages.yaml'
MOCK_TEMPLATE_CONTENTS = 'TEST={{ test_template_parameter }}'
MOCK_PACKAGES_FILE = 'packages.yaml'
MOCK_PACKAGES_CONTENTS = '''PACKAGES = {'test_component':'x'}'''
MOCK_PACKAGES_DICT = {'test_component': 'x'}

HIDE_LEVEL = 'everything'


def file(func):
    @wraps(func)
    def execution_handler(*args, **kwargs):
        client = utils.Handler()
        client.rmdir(TEST_DIR)
        client.mkdir(TEST_DIR)
        sh.touch(TEST_FILE)
        func(*args, **kwargs)
        client.rmdir(TEST_DIR)

    return execution_handler


def dir(func):
    @wraps(func)
    def execution_handler(*args, **kwargs):
        client = utils.Handler()
        client.rmdir(TEST_DIR)
        client.mkdir(TEST_DIR)
        func(*args, **kwargs)
        client.rmdir(TEST_DIR)

    return execution_handler


def venv(func):
    @wraps(func)
    def execution_handler(*args, **kwargs):
        client = py.Handler()
        client.install(['virtualenv'])
        client.make_venv(TEST_VENV)
        func(*args, **kwargs)
        client.rmdir(TEST_VENV)

    return execution_handler


def mock_template(func):
    @wraps(func)
    def execution_handler(*args, **kwargs):
        client = utils.Handler()
        template_file = TEST_TEMPLATES_DIR + '/' + TEST_TEMPLATE_FILE
        client.mkdir(TEST_TEMPLATES_DIR)
        with open(template_file, 'w+') as f:
            f.write(MOCK_TEMPLATE_CONTENTS)
        func(*args, **kwargs)
        client.rm(template_file)
    return execution_handler


def mock_packages(func):
    @wraps(func)
    def execution_handler(*args, **kwargs):
        client = utils.Handler()
        packages_file = TEST_TEMPLATES_DIR + '/' + MOCK_PACKAGES_FILE
        client.mkdir(TEST_TEMPLATES_DIR)
        with open(packages_file, 'w+') as f:
            f.write(MOCK_PACKAGES_CONTENTS)
        func(*args, **kwargs)
        client.rm(packages_file)
        client.rm(packages_file + 'c')
    return execution_handler


class UtilsHandlerTest(testtools.TestCase, utils.Handler):

    def test_get_distro(self):
        test_distro = dist()[0]
        distro = utils.get_distro()
        self.assertEqual(distro, test_distro)

    def test_check_distro_success(self):
        utils.check_distro()

    def test_check_distro_fail(self):
        ex = self.assertRaises(
            SystemExit, utils.check_distro, supported='nodistro')
        self.assertEqual(ex.message, codes.mapping['distro not supported'])

    def test_make_dir(self):
        self.mkdir(TEST_DIR)
        self.assertTrue(os.path.isdir(TEST_DIR))
        self.assertIsNone(self.rmdir(TEST_DIR))

    @dir
    def test_make_dir_already_exists(self):
        self.mkdir(TEST_DIR)
        self.assertTrue(os.path.isdir(TEST_DIR))

    @dir
    def test_make_impossible_dir(self):
        ex = self.assertRaises(SystemExit, self.mkdir, '/impossible')
        self.assertEqual(ex.message, codes.mapping['failed_to_mkdir'])

    @dir
    def test_remove_dir(self):
        self.rmdir(TEST_DIR)
        self.assertFalse(os.path.isdir(TEST_DIR))

    def test_remove_nonexistent_dir(self):
        outcome = self.rmdir(TEST_DIR)
        self.assertFalse(outcome)
        self.assertFalse(os.path.isdir(TEST_DIR))

    @file
    def test_remove(self):
        self.rm(TEST_FILE)
        self.assertFalse(os.path.isfile(TEST_FILE))

    def test_remove_nonexistent_file(self):
        outcome = self.rm(TEST_FILE)
        self.assertFalse(outcome)
        self.assertFalse(os.path.isfile(TEST_FILE))

    @file
    def test_copy(self):
        self.cp(TEST_FILE, '.')
        self.assertTrue(os.path.isfile('./' + TEST_FILE_NAME))
        self.assertIsNone(self.rm(TEST_FILE_NAME))

    def test_copy_noexistent_file(self):
        outcome = self.cp(TEST_FILE, '.')
        self.assertFalse(outcome)
        self.assertFalse(os.path.isfile('./' + TEST_FILE_NAME))

    @dir
    def test_chdir(self):
        cwd = os.getcwd()
        with utils.chdir(TEST_DIR):
            self.assertEqual(os.getcwd(), TEST_DIR)
        self.assertEqual(cwd, os.getcwd())

    @dir
    def test_move(self):
        sh.touch(TEST_FILE_NAME)
        self.mv(TEST_FILE_NAME, TEST_DIR)
        self.assertTrue(os.path.isfile(os.path.join(TEST_DIR, TEST_FILE_NAME)))

    def test_retry(self):
        @utils.retry(retries=2, delay_multiplier=1, backoff=2)
        def bad_action():
            sys.exit(1)
        ex = self.assertRaises(SystemExit, bad_action)
        self.assertEqual(ex.message, 1)

    def test_retry_retries_less_than_zero(self):
        @utils.retry(-1)
        def bad_action():
            sys.exit(1)
        ex = self.assertRaises(ValueError, bad_action)
        self.assertEqual(ex.message, 'retries must be at least 0')

    def test_retry_delay_less_than_zero(self):
        @utils.retry(delay_multiplier=0)
        def bad_action():
            sys.exit(1)
        ex = self.assertRaises(ValueError, bad_action)
        self.assertEqual(ex.message, 'delay_multiplier must be larger than 0')

    def test_retry_backoff_less_than_one(self):
        @utils.retry(backoff=1)
        def bad_action():
            sys.exit(1)
        ex = self.assertRaises(ValueError, bad_action)
        self.assertEqual(ex.message, 'backoff must be greater than 1')

    @log_capture()
    def test_set_global_verbosity_level(self, capture):
        lgr = logger.init(base_level=logging.INFO)

        utils.set_global_verbosity_level(is_verbose_output=False)
        lgr.debug('TEST_LOGGER_OUTPUT')
        capture.check()
        lgr.info('TEST_LOGGER_OUTPUT')
        capture.check(('user', 'INFO', 'TEST_LOGGER_OUTPUT'))

        utils.set_global_verbosity_level(is_verbose_output=True)
        lgr.debug('TEST_LOGGER_OUTPUT')
        capture.check(
            ('user', 'INFO', 'TEST_LOGGER_OUTPUT'),
            ('user', 'DEBUG', 'TEST_LOGGER_OUTPUT'))

    # @file
    # def test_tar(self):
    #     outcome = self.tar('.', './' + TEST_FILE_NAME, TEST_DIR)
    #     self.assertTrue(outcome.succeeded)
    #     self.assertTrue(self.is_file('./' + TEST_FILE_NAME))
    #     self.assertTrue(self.rm('./' + TEST_FILE_NAME).succeeded)

    # def test_tar_bad_options(self):
    #     with hide(HIDE_LEVEL):
    #         outcome = self.tar('.', './' + TEST_FILE_NAME, TEST_DIR,
    #                            'ttt')
    #     self.assertTrue(outcome.failed)
    #     self.assertFalse(self.is_file('./' + TEST_FILE_NAME))


class PythonHandlerTest(testtools.TestCase, py.Handler, utils.Handler):

    def test_pip_existent_module(self):
        self.install([TEST_MODULE])

    def test_pip_nonexistent_module(self):
        ex = self.assertRaises(
            SystemExit, self.install, [TEST_MISSING_MODULE], timeout=2)
        self.assertEqual(
            ex.message, codes.mapping['module_could_not_be_installed'])

    @venv
    def test_pip_existent_module_in_venv(self):
        self.install([TEST_MODULE], TEST_VENV)

    @venv
    def test_pip_nonexistent_module_in_venv(self):
        ex = self.assertRaises(
            SystemExit, self.install, [TEST_MISSING_MODULE],
            TEST_VENV, timeout=2)
        self.assertEqual(
            ex.message, codes.mapping['module_could_not_be_installed'])

    def test_check_module_not_installed(self):
        outcome = self.check_module_installed(TEST_MISSING_MODULE)
        self.assertFalse(outcome)

    def test_check_module_installed(self):
        self.install([TEST_MODULE])
        outcome = self.check_module_installed(TEST_MODULE)
        self.assertTrue(outcome)

    def test_get_module(self):
        cwd = os.getcwd()
        self.get_modules([TEST_MODULE], cwd)
        found = [f for f in os.listdir(cwd) if f.startswith(TEST_MODULE)]
        self.assertTrue(len(found) > 0)
        os.remove(found[0])

    def test_get_nonexisting_module(self):
        cwd = os.getcwd()
        ex = self.assertRaises(
            SystemExit, self.get_modules, [TEST_MISSING_MODULE],
            cwd, timeout=2)
        self.assertEqual(
            ex.message, codes.mapping['failed_to_download_module'])


class RetrieveHandlerTest(testtools.TestCase, retr.Handler, utils.Handler):

    @dir
    def test_download_file_to_dir(self):
        self.downloads([TEST_DL_FILE], dir=TEST_DIR)
        self.assertTrue(os.path.isfile('{0}/master.zip'.format(TEST_DIR)))

    @dir
    def test_download_deb_to_dir(self):
        self.downloads([TEST_DL_DEB], dir=TEST_DIR)
        found = [f for f in os.listdir(
            os.path.join(TEST_DIR, 'archives')) if f.startswith('wget')]
        self.assertTrue(len(found) > 0)

    @dir
    def test_download_file_to_file(self):
        self.download(TEST_DL_FILE, file=TEST_FILE)
        self.assertTrue(os.path.isfile(TEST_FILE))

    def test_download_no_file_no_dir(self):
        ex = self.assertRaises(SystemExit, self.download, TEST_DL_FILE)
        self.assertEqual(ex.message, codes.mapping['must_specify_file_or_dir'])

    def test_download_nonexistent_url(self):
        ex = self.assertRaises(
            SystemExit, self.download,
            'http://www.google.com/x.x', dir=TEST_DIR)
        self.assertEqual(ex.message, codes.mapping['failed_to_download_file'])


class TemplateHandlerTest(testtools.TestCase, templater.Handler,
                          utils.Handler):

    @file
    @mock_template
    def test_template_creation(self):
        component = {'test_template_parameter': 'test_template_output'}
        template_file = TEST_TEMPLATE_FILE
        self.generate_from_template(component, TEST_FILE, template_file,
                                    templates=TEST_TEMPLATES_DIR)
        with open(TEST_FILE, 'r') as f:
            self.assertTrue('test_template_output' in f.read())

    @mock_template
    def test_template_creation_template_file_missing(self):
        component = {'test_template_parameter': 'test_template_output'}
        template_file = 'mock_template'
        try:
            self.generate_from_template(component, TEST_FILE, template_file,
                                        templates=TEST_TEMPLATES_DIR)
        except exc.PackagerError as ex:
            self.assertEqual(str(ex), 'template file missing')

    @mock_template
    def test_template_creation_template_dir_missing(self):
        component = {'test_template_parameter': 'test_template_output'}
        template_file = TEST_TEMPLATE_FILE
        try:
            self.generate_from_template(component, TEST_FILE, template_file,
                                        templates='')
        except exc.PackagerError as ex:
            self.assertEqual(str(ex), 'template dir missing')

    @file
    @mock_template
    def test_template_creation_invalid_component_dict(self):
        component = ''
        template_file = TEST_TEMPLATE_FILE
        try:
            self.generate_from_template(component, TEST_FILE, template_file,
                                        templates=TEST_TEMPLATES_DIR)
        except exc.PackagerError as ex:
            self.assertEqual(str(ex), 'component must be of type dict')

    @file
    @mock_template
    def test_template_creation_template_file_not_string(self):
        component = {'test_template_parameter': 'test_template_output'}
        template_file = False
        try:
            self.generate_from_template(component, TEST_FILE, template_file,
                                        templates=TEST_TEMPLATES_DIR)
        except exc.PackagerError as ex:
            self.assertEqual(str(ex), 'template_file must be of type string')

    @file
    @mock_template
    def test_template_creation_template_dir_not_string(self):
        component = {'test_template_parameter': 'test_template_output'}
        template_file = TEST_TEMPLATE_FILE
        try:
            self.generate_from_template(component, TEST_FILE, template_file,
                                        templates=False)
        except exc.PackagerError as ex:
            self.assertEqual(str(ex), 'template_dir must be of type string')

    @dir
    @mock_template
    def test_config_generation_from_config_dir(self):
        config_file = TEST_TEMPLATE_FILE
        component = {
            "sources_path": TEST_DIR,
            "test_template_parameter": "test_template_parameter",
            "config_templates": {
                "__config_dir": {
                    "files": TEST_TEMPLATES_DIR,
                    "config_dir": "config",
                }
            }
        }
        self.generate_configs(component)
        with open('{0}/{1}/{2}'.format(component['sources_path'],
                  component['config_templates']['__config_dir']['config_dir'],
                  config_file), 'r') as f:
            self.assertTrue(component['test_template_parameter'] in f.read())

    @dir
    @mock_template
    def test_config_generation_from_template_dir(self):
        config_file = TEST_TEMPLATE_FILE
        component = {
            "sources_path": TEST_DIR,
            "test_template_parameter": "test_template_output",
            "config_templates": {
                "__template_dir": {
                    "templates": TEST_TEMPLATES_DIR,
                    "config_dir": "config",
                }
            }
        }
        self.generate_configs(component, sudo=False)
        with open('{0}/{1}/{2}'.format(component['sources_path'],
                  component['config_templates']['__template_dir']['config_dir'],  # NOQA
                  config_file.split('.')[0:-1][0]), 'r') as f:
            self.assertTrue(component['test_template_parameter'] in f.read())

    @dir
    @mock_template
    def test_config_generation_from_template_file(self):
        config_file = TEST_TEMPLATE_FILE
        component = {
            "sources_path": TEST_DIR,
            "test_template_parameter": "test_template_output",
            "config_templates": {
                "__template_file": {
                    "template": TEST_TEMPLATES_DIR + '/' + config_file,
                    "output_file": config_file.split('.')[0:-1][0],
                    "config_dir": "config",
                }
            }
        }
        self.generate_configs(component, sudo=False)
        with open('{0}/{1}/{2}'.format(component['sources_path'],
                  component['config_templates']['__template_file']['config_dir'],  # NOQA
                  config_file.split('.')[0:-1][0]), 'r') as f:
            self.assertTrue(component['test_template_parameter'] in f.read())


class TestBaseMethods(testtools.TestCase):

    @log_capture()
    def test_logger(self, capture):
        lgr = logger.init(base_level=logging.DEBUG)
        lgr.debug('TEST_LOGGER_OUTPUT')
        capture.check(('user', 'DEBUG', 'TEST_LOGGER_OUTPUT'))

    def test_logger_bad_config(self):
        try:
            logger.init(logging_config={'x': 'y'})
        except SystemExit as ex:
            self.assertTrue('could not init' in str(ex))

    def test_get_package_config_dict(self):
        c = packman.get_package_config('test_component', MOCK_PACKAGES_DICT)
        self.assertEqual(c, 'x')

    def test_get_package_config_dict_missing_component(self):
        ex = self.assertRaises(
            SystemExit, packman.get_package_config,
            'WRONG', MOCK_PACKAGES_DICT)
        self.assertEqual(
            ex.message, codes.mapping['no_config_found_for_package'])

    def test_get_package_config_file(self):
        c = packman.get_package_config(
            'mock_package', packages_file=TEST_PACKAGES_FILE)
        self.assertEqual(c['name'], 'test_package')

    def test_get_package_config_file_missing_component(self):
        ex = self.assertRaises(
            SystemExit, packman.get_package_config,
            'WRONG', packages_file=TEST_PACKAGES_FILE)
        self.assertEqual(
            ex.message, codes.mapping['no_config_found_for_package'])

    def test_get_package_config_missing_file(self):
        ex = self.assertRaises(
            SystemExit, packman.get_package_config,
            'test_component', packages_file='x')
        self.assertEqual(
            ex.message, codes.mapping['cannot_access_config_file'])

    # @dir
    # def test_pack(self):
    #     template_file = TEST_TEMPLATE_FILE
    #     config_file = TEST_TEMPLATE_FILE
    #     component = {
    #         "name": "test_package",
    #         "version": "3.0.0",
    #         "depends": [
    #             'test_dependency',
    #         ],
    #         "package_path": TEST_DIR,
    #         "sources_path": TEST_DIR + '/test_sources_dir',
    #         "src_package_type": "dir",
    #         "dst_package_type": "deb",
    #         # "bootstrap_script": 'bootstrap_script.sh',
    #         # "bootstrap_template": template_file,
    #         "config_templates": {
    #             "__template_file": {
    #                 "template": TEST_TEMPLATES_DIR + '/' + config_file,
    #                 "output_file": config_file.split('.')[0:-1][0],
    #                 "config_dir": "config",
    #             },
    #             # "__template_dir": {
    #             #     "templates": TEST_TEMPLATES_DIR,
    #             #     "config_dir": "config",
    #             # },
    #             # "__config_dir": {
    #             #     "files": TEST_TEMPLATES_DIR,
    #             #     "config_dir": "config",
    #             # }
    #         }
    #     }
    #     pack(component)

# TODO: (TEST) add apt handler tests
# TODO: (TEST) add yum handler tests (hrm.. how to?)
