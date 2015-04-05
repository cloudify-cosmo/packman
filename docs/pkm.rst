===================
pkm - packman's CLI
===================

CLI Functionality
-----------------
``packman``'s provides a cli interface to packman's basic features.
you can:

.. note:: the below commands also apply to ``get`` (retrieving sources).

- pack all packages in a ``packages file`` (pkm pack)
- pack a single package (pkm pack -c package_NAME)
- pack a list of packages (pkm pack -c package1,package2,package3...)
- pack packages from an alternative ``packages file`` (pkm pack -f /my_packages_file.yaml)
- pack packages with an exclusion list (pkm pack -x packageS1,package2,...)
- perform all of the above on ``get`` and ``pack`` using the same command (pkm make)
- using the basic implementation of the get and pack methods for all packages in a packages file and specifying a list of packages for packman to iterate over to getting and packing a package (or all packages) in a single command.

running::

    pkm -h

yeilds the following::

    Script to run packman via command line

    Usage:
        pkm get [--packages=<list> --packages-file=<path> --exclude=<list> -v]
        pkm pack [--packages=<list> --packages-file=<path> --exclude=<list> -v]
        pkm make [--packages=<list> --packages-file=<path> --exclude=<list> -v]
        pkm --version

    Arguments:
        pack     Packs package configured in packages file
        get      Gets package configured in packages file
        make     Gets AND (yeah!) Packs.. don't ya kno!

    Options:
        -h --help                   Show this screen.
        -c --packages=<list>      Comma Separated list of package names
        -x --exclude=<list>         Comma Separated list of excluded packages
        -f --packages-file=<path> packages file path
        -v --verbose                a LOT of output
        --version                   Display current version of sandman and exit

.. note:: when not specifying copmonents explicitly using the --packages flag, the task will run on all packages in the dict.