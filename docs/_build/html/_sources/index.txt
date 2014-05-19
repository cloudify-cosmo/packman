Welcome to packman's documentation!
===================================
packman creates packages.

packman retrieves sources, maybe adds some bootstrap scripts and configuration files to them, and packs them up nice and tight in a single package.

packman's real strength is in providing an simple configuration based API to the most basic tasks in creating packages like:

- retrieving sources from apt, yum, ppa and urls.
- retrieving python modules and ruby gems WITH dependencies.
- generating different files from templates using jinja2.
- packaging using fpm (API NOT IMPLEMENTED YET - only exists in default implementation).
- handling different file operations like creating directories and removing them, taring, untaring, etc..

additionally, you can create your own python based tasks to replace the default ones and call them very simply using pkm (packman's cli).

Contents:

.. toctree::
   :maxdepth: 2

   quick_start
   installation
   pkm
   component_config
   template_handling
   alternative_methods
   api
   module_file_struct


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

