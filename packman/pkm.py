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

"""Script to run packman via command line

Usage:
    pkm get [--components=<list> --components-file=<path> --exclude=<list>]
    pkm pack [--components=<list> --components-file=<path> --exclude=<list>]
    pkm make [--components=<list> --components-file=<path> --exclude=<list>]
    pkm --version

Arguments:
    pack     Packs component configured in components file
    get      Gets component configured in components file
    make     Gets AND (yeah!) Packs.. don't ya kno!

Options:
    -h --help                   Show this screen.
    -c --components=<list>      Comma Separated list of component names
    -x --exclude=<list>         Comma Separated list of excluded components
    -f --components-file=<path> Components file path
    --verbose                   a LOT of output (NOT YET IMPLEMENTED)
    -v --version                Display current version of sandman and exit

"""

from __future__ import absolute_import
from docopt import docopt
from platform import dist
from sys import exit

from packman.packman import packman_runner

dist_list = ('Ubuntu', 'debian', 'centos')


def check_dist():
    distro = dist()[0]
    print('Distribution Identified: {}'.format(distro))
    if not distro in dist_list:
        print('Your distribution is not supported.'
              'Supported Disributions are:')
        for distro in dist_list:
            print('    {}'.format(distro))
        exit(1)


def main(test_options=None):
    """Main entry point for script."""
    # TODO: currently, distrib is checked thruout the code. change it to once.
    check_dist()
    import pkg_resources
    version = None
    try:
        version = pkg_resources.get_distribution('packman').version
    except Exception as e:
        print(e)
    finally:
        del pkg_resources

    # TODO: implement verbose output
    options = test_options or docopt(__doc__, version=version)
    print(options)
    if options['pack']:
        packman_runner('pack',
                       options.get('--components-file'),
                       options.get('--components'),
                       options.get('--exclude'))
    elif options['get']:
        packman_runner('get',
                       options.get('--components-file'),
                       options.get('--components'),
                       options.get('--exclude'))
    elif options['make']:
        packman_runner('get',
                       options.get('--components-file'),
                       options.get('--components'),
                       options.get('--exclude'))
        packman_runner('pack',
                       options.get('--components-file'),
                       options.get('--components'),
                       options.get('--exclude'))


if __name__ == '__main__':
    main()
