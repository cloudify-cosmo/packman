============
Installation
============

Pre-Requirements
----------------
``packman`` uses the following 3rd party components:

- python-dev -*for pycrypto (ARG!)*
- python-setuptools -*also to install packages on the ``packman`` instance*
- fpm -*main packaging framework*
- fabric -*to run it all*
- pip >1.5 -*to download python modules*
- jinja2 -*to create scripts and configuration files from templates*
- virtualenv (OPTIONAL) -*to create python virtual environments.*
- rubygems (OPTIONAL) -*to download ruby gems*

.. note:: a `script <https://github.com/cloudify-cosmo/packman/blob/develop/vagrant/provision.sh>`_ is provided to install the above requirements.

Installing Packman
------------------
You can install ``packman`` by running ``pip install packman``.
Of course, you must have the prereqs installed to fully utilize ``packman``'s potential...

.. note:: The `vagrantfile <https://github.com/cloudify-cosmo/packman/blob/develop/vagrant/Vagrantfile>`_ provided in the github repo can supply you with a fully working ``packman`` machine.