============
Installation
============

Pre-Requirements
----------------
packman uses the following 3rd party components:

- make -*to... make?*
- python-dev -*for pycrypto (ARG!)*
- python-setuptools -*also to install packages on the packager server*
- rubygems -*to download ruby gems*
- git -*to clone the packager repo*
- fpm -*main packaging framework*
- ruby-build -*to compile ruby*
- fabric -*to run it all*
- pip >1.5 -*to download python modules*
- virtualenv -*to create python virtual environments.*
- jinja2 -*to create scripts and configuration files from templates*
- pika -*to send events to rabbitmq if it's installed on the packaging server (for testing purposes)*
a bootstrap script is provided to install the above packages.

Installing Packman
------------------
You Can Install Packman by running ``pip install https://github.com/cloudify-cosmo/cloudify-packager/archive/master.zip``.
Of course, you must have the prereqs installed for packman to fully utilize its potential...
The vagrantfile provided in the github repo can supply you with a fully working packman machine.

ADD INSTALL-PACKMAN.SH file here to download....