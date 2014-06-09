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
        -v --verbose                a LOT of output
        --version                   Display current version of sandman and exit

.. note:: when not specifying copmonents explicitly using the --components flag, the task will run on all components in the dict.