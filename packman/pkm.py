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
    pkm get [--components=<list> --components-file=<path> --exclude=<list> -v]
    pkm pack [--components=<list> --components-file=<path> --exclude=<list> -v]
    pkm make [--components=<list> --components-file=<path> --exclude=<list> -v]
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
    -v --verbose                a LOT of output (NOT YET IMPLEMENTED)
    --version                   Display current version of sandman and exit

"""

from __future__ import absolute_import
from docopt import docopt
from packman.packman import init_logger
from packman.packman import packman_runner
from packman.packman import check_distro
from packman.packman import set_global_verbosity_level

lgr = init_logger()


def ver_check():
    import pkg_resources
    version = None
    try:
        version = pkg_resources.get_distribution('packman').version
    except Exception as e:
        print(e)
    finally:
        del pkg_resources
    return version


def pkm_run(o):
    if o['pack']:
        packman_runner('pack',
                       o.get('--components-file'),
                       o.get('--components'),
                       o.get('--exclude'),
                       o.get('--verbose'))
    elif o['get']:
        packman_runner('get',
                       o.get('--components-file'),
                       o.get('--components'),
                       o.get('--exclude'),
                       o.get('--verbose'))
    elif o['make']:
        packman_runner('get',
                       o.get('--components-file'),
                       o.get('--components'),
                       o.get('--exclude'),
                       o.get('--verbose'))
        packman_runner('pack',
                       o.get('--components-file'),
                       o.get('--components'),
                       o.get('--exclude'),
                       o.get('--verbose'))


def pkm(test_options=None):
    """Main entry point for script."""
    version = ver_check()
    options = test_options or docopt(__doc__, version=version)
    set_global_verbosity_level(options.get('--verbose'))
    check_distro(verbose=options.get('--verbose'))
    lgr.debug(options)
    pkm_run(options)


def main():
    pkm()


if __name__ == '__main__':
    main()
