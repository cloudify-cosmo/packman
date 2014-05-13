===================
pkm - packman's CLI
===================

CLI Functionality
-----------------
``packman``'s provides a cli interface to packman's basic features.
you can:

.. note:: the below commands also apply to ``get`` (retrieving sources).

- pack all components in a ``components file`` (pkm pack)
- pack a single component (pkm pack -c COMPONENT_NAME)
- pack a list of components (pkm pack -c COMPONENT1,COMPONENT2,COMPONENT3...)
- pack components from an alternative ``components file`` (pkm pack -f /my_components_file.py)
- pack components with an exclusion list (pkm pack -x COMPONENTS1,COMPONENT2,...)
- perform all of the above on ``get`` and ``pack`` using the same command (pkm make)
- using the basic implementation of the get and pack methods for all components in a components file and specifying a list of components for packman to iterate over to getting and packing a component (or all components) in a single command.

running::

    pkm -h

yeilds the following::

    Script to run packman via command line

    Usage:
        pkm get [--components=<list> --components_file=<path> --exclude=<list>]
        pkm pack [--components=<list> --components_file=<path> --exclude=<list>]
        pkm make [--components=<list> --components_file=<path> --exclude=<list>]
        pkm --version

    Arguments:
        pack     Packs "Component" configured in packages.py
        get      Gets "Component" configured in packages.py
        make     Gets AND (yeah!) Packs.. don't ya kno!

    Options:
        -h --help                   Show this screen.
        -c --components=<list>      Comma Separated list of component names
        -x --exclude=<list>         Comma Separated list of excluded components
        -f --components_file=<path> Components file path (if ommited, will assume packages.py in the cwd)
        --verbose                   a LOT of output (NOT YET IMPLEMENTED)
        -v --version                Display current version of sandman and exit