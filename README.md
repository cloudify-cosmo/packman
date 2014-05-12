packman
==============

packman creates packages.

The project was initally invented to create Cloudify (http://getcloudify.org/) packages and is now progressing towards being a good open-source solution to creating different types of packages for different needs.

You can write a dict containing your package's configuration and packman will retrieve the resources and create a package accordingly.

### PreReqs
for a list of reqreqs, please see the docs.

### Installation
NOTE: will be published in PyPi soon... for now..
```shell
pip install https://github.com/cloudify-cosmo/cloudify-packager/archive/develop.tar.gz
```

NOTE: you may use the vagrant file to get a boxed up complete installation of packman..

#### packages.py
packages.py contains the full configuration for all components. when running pkm, you can explicitly specify a packages.py file path. if you don't, a packages.py in your
current working directory is expected.
by applying different files to different directories or different packages.py paths, you can logically separate components and automate the process.
(something like... for file in files_list, pkm make --components_file=file.... you know...)

the packages.py file must contain a variable called *PACKAGES*. *PACKAGES* must be a dict containing the configuration for all relevant components as sub-dicts.

### Usage
packman supplies a cli called "pkm" to run get and pack tasks.
```shell
pkm -h
Script to run packman via command line

Usage:
    pkm get [--components=<list> --components_file=<path>] [--verbose]
    pkm pack [--components=<list> --components_file=<path>] [--verbose]
    pkm make [--components=<list> --components_file=<path>] [--verbose]
    pkm --version

Arguments:
    pack     Packs "Component" configured in packages.py
    get      Gets "Component" configured in packages.py
    make     Gets AND (yeah!) Packs.. don't ya kno!

Options:
    -h --help                   Show this screen.
    -c --components=<list>      Comma Separated list of component names (if ommited, will run on all components)
    --components_file=<path>
    --verbose                   a LOT of output (NOT YET IMPLEMENTED)
    -v --version                Display current version of sandman and exit
```

NOTE: when not specifying copmonents explicitly using the --components flag, the task will run on all components in the dict.

examples:
```shell
pkm get --components my_component --components_file /my_components_file.py
pkm pack -c my_component,my_other_component
pkm make
```


Lets take an example of a component's creation cycle - from retrieval to dpkg-i-ing. We'll look at Riemann:

#### Component config:
NOTE: here's an example of a packages.py file:
```python
    PACKAGES = {
        "riemann": {
            "name": "riemann",
            "version": "0.2.2",
            "source_urls": [
                "http://aphyr.com/riemann/riemann_0.2.2_all.deb",
            ],
            "depends": [
                'openjdk-7-jdk'
            ],
            "package_path": "{0}/riemann/".format(COMPONENT_PACKAGES_PATH),
            "sources_path": "{0}/riemann".format(PACKAGES_PATH),
            "dst_package_type": "deb"
        },
    }
```

##### Component config parameters breakdown:
- ***name*** is the component's name (DUH!). it's used to create named directories and package file names mostly.
- ***version***, when applicable, is used to apply a version to the component's package name (in the future, it might dictate the component's version to download.)
- ***source_urls*** is a list of package sources to download.
- ***depends*** is a list of dependencies for the package (obviously only applicable to specific package types like debs and rpms.)
- ***package_path*** is the path where the component's package will be stored after the packaging process is complete for that same component.
- ***sources_path*** is the path where the component's parts (files, configs, etc..) will be stored before the component's package is created.
- ***dst_package_type*** is... well.. you know.

##### Additional params you might use:
see the docs

#### Component handling:
running *pkm **get** --components riemann*, packman will use wget to download the list of source_urls (only one in this case)
to the sources_path.

it is possible to use a user made get method instead.
if a get.py file exists in the current working directory, and contains a function called "get_#COMPONENT_NAME#", it will be executed instead of the base get method.

of course, a user can create a specific get function only to extend the base get method by importing the ***get*** method from packman and adding to it.

NOTE: the same goes for ***pack*** using the pack.py file.

#### Component templates:
- packman uses python's jinja2 module to create files from templates.
- template files can be used to generate bootstrap scripts or configuration files by default, but can also be used using external pack/get functions (see component handling) to generate other files if relevant.

##### bootstrap script tepmlates:
- Components which should be packaged along with a bootstrap script should have a .template file stationed in package-templates/
- During the packaging process, if a template file exists and its path is passed to the "pack" function (possibly from the config), the bootstrap script will be created and attached to the package (whether by copying it into the package (in case of a tar for instance), or by attaching it (deb, rpm...).)
- The bootstrap script will run automatically upon dpkg-ing when applicable.

Here's an example of a template bootstrap script (for virtualenv, since riemann doesn't require one):

	PKG_NAME="{{ name }}"
	PKG_DIR="{{ sources_path }}"

	echo "extracting ${PKG_NAME}..."
	sudo tar -C ${PKG_DIR} -xvf ${PKG_DIR}/*.tar.gz
	echo "removing tar..."
	sudo rm ${PKG_DIR}/*.tar.gz
	cd ${PKG_DIR}/virtualenv*
	echo "installing ${PKG_NAME}..."
	sudo python setup.py install

The double curly braces are where the variables are eventually assigned.
The name of the variable must match a component's config variable in its dict (e.g name, package_dir, etc...).

##### config templates:
- it is possible to generate configuration file/s from templates or just copy existing configuration files into the package which can later be used by the bootstrap script to deploy the package along with its config.
- the component's "config_templates" sub-dict can be used for that purpose. 4 types of config template keys exist in the sub-dict:
    - __template_dir - a directory from which template files are generated (iterated over...)
    - __template_file - an explicit name from which a template file is generated.
    - __config_dir - a directory from which config files are copied.
    - __config_file - an explicit name of a config file to be copied.

### Vagrant
A vagrantfile is provided to load 2 machines:

- a packman host (which, by default, is prepared for packaging components)
- a tester host (which, by default, is a clean, vagrant version ubuntu machine to test the package installation on)
- CentOS and other distribs are on the way...

##### Automated Vagrant Testing Environment
In future versions, an automated process of retrieval, packaging and installation will be implemented to check the entire process.
