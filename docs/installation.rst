============
Installation
============

Pre-Requirements
----------------
``packman`` uses the following 3rd party components:

- ruby - *required for fpm*
- fpm -*main packaging framework*
- pip >1.5 -*to download python modules (and install packman)*
- virtualenv (OPTIONAL) -*to create python virtual environments.*
- rubygems (OPTIONAL) -*to download ruby gems*
- rpmbuild (OPTIONAL) -*to create rpms*
- tar (OPTIONAL) -*to create tars*
- gzip (OPTIONAL) -*to create tar.gz's*

.. note:: the rest of the requirements are python modules which will be installed with `packman`

.. note:: a `script <https://github.com/cloudify-cosmo/packman/blob/master/vagrant/provision.sh>`_ is provided to install the above requirements.

Installing Packman
------------------
You can install ``packman`` by running ``pip install packman``.
Of course, you must have the prereqs installed to fully utilize ``packman``'s potential...

.. note:: The `vagrantfile <https://github.com/cloudify-cosmo/packman/blob/master/vagrant/Vagrantfile>`_ provided in the github repo can supply you with a fully working ``packman`` machine.