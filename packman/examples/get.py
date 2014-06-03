#!/usr/bin/env python
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

from packman.packman import init_logger
from packman.packman import get_component_config as get_conf
from packman.packman import CommonHandler
from packman.packman import WgetHandler
from packman.packman import do

from fabric.api import *  # NOQA

lgr = init_logger()

# __all__ = ['list']


def _prepare(package):

    common = CommonHandler()
    common.rmdir(package['sources_path'])
    # DEPRACATE!
    common.make_package_paths(
        package['package_path'],
        package['sources_path'])


def get_elasticsearch():
    """
    ACT:    retrives elasticsearch
    EXEC:   fab get_elasticsearch
    """

    package = get_conf('elasticsearch')

    dl_handler = WgetHandler()
    _prepare(package)
    for url in package['source_urls']:
        dl_handler.download(url, dir=package['sources_path'])


def get_kibana():
    """
    ACT:    retrives kibana
    EXEC:   fab get_kibana
    """

    package = get_conf('kibana3')

    dl_handler = WgetHandler()
    _prepare(package)
    for url in package['source_urls']:
        dl_handler.download(url, dir=package['sources_path'])


def get_ruby():
    """
    ACT:    retrives ruby
    EXEC:   fab get_ruby
    """

    package = get_conf('ruby')

    _prepare(package)
    with lcd('/opt'):
        do('git clone '
           'https://github.com/sstephenson/ruby-build.git')
    do('export PREFIX=/opt/ruby-build', sudo=False)
    do('/opt/ruby-build/install.sh')
    do('/opt/ruby-build/bin/ruby-build -v {} {}'.format(
        package['version'], package['sources_path']))
