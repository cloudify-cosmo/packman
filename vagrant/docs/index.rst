.. packman documentation master file, created by
   sphinx-quickstart on Thu Apr  3 23:59:36 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to packman's documentation!
===================================
packman creates packages.

packman retrieve sources, adds some bootstrap scripts and configuration files to them, and packs them up nice and tight in a single package for different distros.

packman's real strength is in providing an simple configuration based API to the most basic tasks in creating packages like:

- retrieving sources from apt, yum and urls.
- retrieving python modules and ruby gems WITH dependencies from pypi or github.
- generating different files from templates using jinja2
- packaging using fpm (API NOT IMPLEMENTED YET - only exists in default implementation)
- handling different file operations like creating directories, removing them, taring, untaring, etc..

additionally, you can create your own python based tasks to replace the default ones and call them very simply using pkm (packman's cli).

Contents:

.. toctree::
   :maxdepth: 2

   quick_start
   installation
   pkm
   component_config
   api
   alternative_methods
   module_file_struct


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

