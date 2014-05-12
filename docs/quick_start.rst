quick_start.rst

============
Quick Start
============

- install vagrant
- install virtualbox
- clone the github repo::
    git clone git@github.com:cloudify-cosmo/cloudify-packager.git
- go to the vagrant directory
- run::
    vagrant up packman
    vagrant ssh packman
    cd ~/examples
    sudo su
    pkm get
    pkm pack

review the retrieved resources in /sources
review the created deb files in /packages