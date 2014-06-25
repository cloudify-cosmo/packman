============
Installation
============

Pre-Requirements
----------------
``packman`` uses the following 3rd party components:

- python-dev -*for pycrypto (ARG!)*
- python-setuptools -*also to install packages on the ``packman`` instance*
- ruby - *required for fpm*
- fpm -*main packaging framework*
- pip >1.5 -*to download python modules (and install packman)*
- virtualenv (OPTIONAL) -*to create python virtual environments.*
- rubygems (OPTIONAL) -*to download ruby gems*

.. note:: the rest of the requirements are python modules which will be installed with `packman`

.. note:: a `script <https://github.com/cloudify-cosmo/packman/blob/develop/vagrant/provision.sh>`_ is provided to install the above requirements.

Installing Packman
------------------
You can install ``packman`` by running ``pip install packman``.
Of course, you must have the prereqs installed to fully utilize ``packman``'s potential...

.. note:: The `vagrantfile <https://github.com/cloudify-cosmo/packman/blob/develop/vagrant/Vagrantfile>`_ provided in the github repo can supply you with a fully working ``packman`` machine.