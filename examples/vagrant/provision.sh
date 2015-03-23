function install_prereqs
{
    # ubuntu
    sudo apt-get -y update &&
    # precise
    sudo apt-get install -y python-software-properties ||
    # trusty
    sudo apt-get install -y software-properties-common &&
    sudo add-apt-repository -y ppa:git-core/ppa &&
    sudo apt-get install -y curl python-dev git make gcc libyaml-dev zlib1g-dev g++
}

function install_ruby
{
    wget https://ftp.ruby-lang.org/pub/ruby/ruby-1.9.3-rc1.tar.bz2 --no-check-certificate
    tar -xjf ruby-1.9.3-rc1.tar.bz2
    cd ruby-1.9.3-rc1
    ./configure --disable-install-doc
    make
    sudo make install
    cd ~
}

function install_fpm
{
    sudo gem install fpm --no-ri --no-rdoc
    # if we want to downlod gems as a part of the packman run, this should be enabled
    # echo -e 'gem: --no-ri --no-rdoc\ninstall: --no-rdoc --no-ri\nupdate:  --no-rdoc --no-ri' >> ~/.gemrc
}

function install_pip
{
    curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python
}

function install_module
{

    module=$1
    venv=${2:-""}
    tag=${3:-""}
    if [[ ! -z "$tag" ]]; then
        org=${4:-cloudify-cosmo}
        url=https://github.com/${org}/${module}.git
        echo cloning ${url}
        git clone ${url}
        pushd ${module}
            git checkout -b tmp_branch ${tag}
            git log -1
            sudo ${venv}/bin/pip install .
        popd
    else
        if [[ ! -z "$venv" ]]; then
            # if [[ ! -z "$tag" ]]; then
            #   pip install git+git://github.com/${org}/${module}.git@${tag}#egg=${module}
            # else
            sudo ${venv}/bin/pip install ${module}
            # fi
        else
            sudo pip install ${module}
        fi
    fi
}

AGENT=$1
CORE_TAG_NAME="master"
PLUGINS_TAG_NAME="master"

install_prereqs &&
if ! which ruby; then
    install_ruby
fi
install_fpm &&
install_pip &&
install_module "https://github.com/cloudify-cosmo/packman/archive/pkm-overhaul.zip" &&
install_module "virtualenv==12.0.7" &&

cd /cloudify-packager/ &&
