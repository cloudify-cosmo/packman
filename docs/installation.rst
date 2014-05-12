============
Installation
============

Pre-Requirements
----------------
``packman`` uses the following 3rd party components:

- make -*to... make?* (DEPRACATE PLEASE!)
- python-dev -*for pycrypto (ARG!)*
- python-setuptools -*also to install packages on the ``packman`` instance*
- rubygems -*to download ruby gems*
- git -*to clone the packager repo, and maybe more! (Chandler Bing)*
- fpm -*main packaging framework*
- fabric -*to run it all*
- pip >1.5 -*to download python modules*
- virtualenv -*to create python virtual environments.*
- jinja2 -*to create scripts and configuration files from templates*
- pika -*to send events to rabbitmq if it's installed on the packaging server (for testing purposes)*

a `script <https://github.com/cloudify-cosmo/packman/blob/develop/vagrant/provision.sh>`_ is provided to install the above packages.

Installing Packman
------------------
You can install ``packman`` by running ``pip install https://github.com/cloudify-cosmo/cloudify-packager/archive/master.zip``.
Of course, you must have the prereqs installed for packman to fully utilize its potential...
The `vagrantfile <https://github.com/cloudify-cosmo/packman/blob/develop/vagrant/Vagrantfile>`_ provided in the github repo can supply you with a fully working ``packman`` machine.