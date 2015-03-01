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
    pkm get [--packages=<list> --packages-file=<path> --exclude=<list> -v]
    pkm pack [--packages=<list> --packages-file=<path> --exclude=<list> -v]
    pkm make [--packages=<list> --packages-file=<path> --exclude=<list> -v]
    pkm --version

Arguments:
    pack     Creates packages configured in packages file
    get      Retrives resources for package configured in packages file
    make     Gets AND (yeah!) Packs.. don't ya kno!

Options:
    -h --help                   Show this screen.
    -c --packages=<list>        Comma Separated list of package names
    -x --exclude=<list>         Comma Separated list of excluded packages
    -f --packages-file=<path> packages file path
    -v --verbose                a LOT of output
    --version                   Display current version of package and exit

"""

from __future__ import absolute_import
from docopt import docopt
from packman import logger
from packman.packman import packman_runner
from packman.utils import check_distro
from packman import utils

lgr = logger.init()


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
                       o.get('--packages-file'),
                       o.get('--packages'),
                       o.get('--exclude'),
                       o.get('--verbose'))
    elif o['get']:
        packman_runner('get',
                       o.get('--packages-file'),
                       o.get('--packages'),
                       o.get('--exclude'),
                       o.get('--verbose'))
    elif o['make']:
        packman_runner('get',
                       o.get('--packages-file'),
                       o.get('--packages'),
                       o.get('--exclude'),
                       o.get('--verbose'))
        packman_runner('pack',
                       o.get('--packages-file'),
                       o.get('--packages'),
                       o.get('--exclude'),
                       o.get('--verbose'))


def pkm(test_options=None):
    """Main entry point for script."""
    version = ver_check()
    options = test_options or docopt(__doc__, version=version)
    utils.set_global_verbosity_level(options.get('--verbose'))
    check_distro(verbose=options.get('--verbose'))
    lgr.debug(options)
    pkm_run(options)


def main():
    pkm()


if __name__ == '__main__':
    main()
