======================
Packman File Structure
======================

Module
------
- packman.py contains the base functions and classes for handling component actions (pack, get, wget, mkdir, apt-download, etc..).
- packman_config.py contains the packman logger configuration.
- event_handler.py providers an interface to rabbitmq (EXPERIMENTAL and currently in development)
- definitons.py contains the base parameter definitions for the components file.
- packages.py in the current working directory contains a PACKAGES dict param with the component's configuration.

User
----
- components file other than packages.py (optional) can be stationed anywhere as long as they're addressed thru the cli.
- get.py in the current working directory (optional) contains the logic for downloading and arranging a component's contents.
- pack.py in the current working directory (optional) contains the logic for packaging a component.
- if bootstrap scripts exist, a "package-templates" directory must exist in the current working directory (will be changed in the future...)
- of course, any other directories and files can co-exist in the current working directory. for instance, a package-configuration directory can be created and then referenced in the components file to hold package configuration file templates.