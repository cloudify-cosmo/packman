quick_start.rst

============
Quick Start
============

- install `Vagrant <http://www.vagrantup.com/downloads.html>`_.
- install `VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_.
- clone the github repo::

    git clone git@github.com:cloudify-cosmo/cloudify-packager.git

- go to the vagrant directory
- run::

    vagrant up packman
    vagrant ssh packman
    cd ~/examples
    sudo su
    pkm make

- review the retrieved resources in /sources
- review the created deb files in /packages
