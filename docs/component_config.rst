===========================
Packages File Configuration
===========================

Configuration of all packages is done via a YAML file containing a single dict with multiple (per package) sub-dicts.
We will call it the ``packages file``.
An example `packages <https://github.com/cloudify-cosmo/packman/blob/master/packman/tests/resources/packages.yaml>`_ file can get you started...

A package's Structure
-----------------------
A package is comprised of a set of key:value pairs.
Each package has a set of mandatory parameters like name and version and of optional parameters like source_urls.

A very simple example of a package's configuration::

    packages:
    mock_package:
        name: test_package
        version: 3.1
        sources_path: sources
        depends:
            - make
            - g++
        prereqs:
            - curl
        source_ppas:
            - ppa:chris-lea/node.js
        source_repos:
            - deb http://nginx.org/packages/mainline/ubuntu/ precise nginx
            - deb-src http://nginx.org/packages/mainline/ubuntu/ precise nginx
        source_keys:
            - http://nginx.org/keys/nginx_signing.key
        source_urls:
            - https://github.com/jaraco/path.py/archive/master.zip
        requires:
            - make
        virtualenv:
            path: venv
            modules:
                - pyyaml
        python_modules:
            - nonexistentmodule
            - cloudify
            - pyyaml
        ruby_gems:
            - gosu
        package_path: tests
        source_package_type: dir
        destination_package_types:
            - tar.gz
            - deb
            - rpm
        keep_sources: true
        bootstrap_script: packman/tests/templates/mock_template.j2
        bootstrap_template:
        test_template_parameter: test_template_output
        config_templates:
            template_file:
                template: packman/tests/templates/mock_template.j2
                output_file: mock_template.output
                config_dir: config
            template_dir:
                templates: packman/tests/templates
                config_dir: config
            config_dir:
                files: packman/tests/templates
                config_dir: config
            params: param

Breakdown:

    - ***name*** is the package's name (DUH!). it's used to create named directories and package file names mostly.
    - ***version***, when applicable, is used to apply a version to the package's package name (in the future, it might dictate the package's version to download.)
    - ***sources_path*** is the path where the package's parts (files, configs, etc..) will be stored before the package's package is created.
    - ***depends*** is a list of dependencies for the package (obviously only applicable to specific package types like debs and rpms.)
    - ***prereqs*** is a list of distribution specific requirements to install before attemping to retrieve the package's resources.
    - ***source_ppas*** is a list of ppa repos to add.
    - ***source_repos*** is a list of repositories to add to the local repos file (distro specific).
    - ***source_keys*** is a list of keys to add.
    - ***source_urls*** is a list of package sources to download.
    - ***requires*** is a list of distro specific requirements to download (from apt, yum, etc..)
    - ***package_path*** is the path where the package's package will be stored after the packaging process is complete for that same package.
    ... meh.
    - ***destination_package_types*** is... well.. you know.

Additional Configuration Parameters
-----------------------------------
By default, a package can be comprised of a set of parameters, all of which (names) are configurable in the definitions.py file (This is currently only available by editing the module directly). The file is not currently directly available to the user (as most of the parameters names are self-explanatory) but at a future version, a user will be able to override the parameter names by supplying an overriding definitions.py file (to override all or some of the parameter names).

For the complete list of params, see the `defintions <https://github.com/cloudify-cosmo/packman/blob/master/packman/definitions.py>`_ file.