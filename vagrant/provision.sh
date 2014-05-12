echo bootstrapping...

# update
sudo apt-get -y update &&

# install prereqs
sudo apt-get install -y vim make git &&
sudo apt-get install -y python-setuptools python-dev &&
sudo apt-get install -y rubygems &&
sudo gem install fpm --no-ri --no-rdoc &&
# sudo wget https://bootstrap.pypa.io/get-pip.py -P ~/
# sudo python ~/get-pip.py
sudo apt-get purge pip
sudo easy_install -U pip &&
sudo wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | sudo python &&
sudo pip install virtualenv==1.11.4 jinja2==2.7.2 pika==0.9.13 fabric==1.8.3 &&

# configure gem and bundler
echo -e 'gem: --no-ri --no-rdoc\ninstall: --no-rdoc --no-ri\nupdate:  --no-rdoc --no-ri' >> ~/.gemrc

# add fabric bash completion
cd /vagrant &&
sudo wget https://github.com/marcelor/fabric-bash-autocompletion/raw/master/fab
sudo mv fab /etc/bash_completion.d/
echo 'source /etc/bash_completion.d/fab' >> ~/.bashrc &&

# TODO: add virtualenv
# sudo pip install virtualenvwrapper
# mkvirtualenv packman
sudo pip install https://github.com/cloudify-cosmo/cloudify-packager/archive/feature/CFY-516-packman-opensource-phase2.tar.gz
# TODO: add bash completion support using docopt-completion
# docopt-completion #VIRTUALENV#...pkm.py
# source ~/.bashrc

echo bootstrap done
echo NOTE: currently, using some of the packman's features requires that they're run as sudo.