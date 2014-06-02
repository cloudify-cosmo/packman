echo bootstrapping packman...

# update
sudo apt-get -y update &&
# install prereqs
sudo apt-get install -y python-setuptools python-dev rubygems &&
# install fpm
sudo gem install fpm --no-ri --no-rdoc &&
# configure gem and bundler
echo -e 'gem: --no-ri --no-rdoc\ninstall: --no-rdoc --no-ri\nupdate:  --no-rdoc --no-ri' >> ~/.gemrc
# install pip
sudo apt-get purge pip
sudo easy_install -U pip &&
sudo wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | sudo python &&
# install virtualenv
sudo pip install virtualenv==1.11.4 &&
# install packman
sudo pip install https://github.com/cloudify-cosmo/packman/archive/develop.tar.gz
# TODO: add virtualenv to provisioning process
# sudo pip install virtualenvwrapper
# mkvirtualenv packman
# TODO: add bash completion support using docopt-completion
# docopt-completion #VIRTUALENV#...pkm.py

echo bootstrap done
echo NOTE: currently, using some of the packman's features requires that it's run as sudo.