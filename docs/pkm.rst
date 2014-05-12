===================
pkm - packman's CLI
===================

CLI Functionality
-----------------
packman's cli provides a comprehensive interface to packman's features.
you can do anything from using the basic implementation of the get and pack methods for all components in a components file and specifying a list of components for packman to iterate over to getting and packing a component (or all components) in a single command.

running::

    pkm -h

yeilds the following::

    Script to run packman via command line

    Usage:
        pkm get [--components=<list> --components_file=<path>] [--verbose]
        pkm pack [--components=<list> --components_file=<path>] [--verbose]
        pkm make [--components=<list> --components_file=<path>] [--verbose]
        pkm --version

    Arguments:
        pack     Packs "Component" configured in packages.py
        get      Gets "Component" configured in packages.py
        make     Gets AND (yeah!) Packs.. don't ya kno!

    Options:
        -h --help                   Show this screen.
        -c --components=<list>      Comma Separated list of component names (if ommited, will run on all components)
        --components_file=<path>
        --verbose                   a LOT of output (NOT YET IMPLEMENTED)
        -v --version                Display current version of sandman and exit
