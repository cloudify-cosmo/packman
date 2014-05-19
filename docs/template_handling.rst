========================================================
Template Handling
========================================================

Component templates:

- packman uses python's jinja2 module to create files from templates.
- template files can be used to generate bootstrap scripts or configuration files by default, but can also be used using external pack/get functions (see component handling) to generate other files if relevant.

Bootstrap script tepmlates:

- Components which should be packaged along with a bootstrap script should have a .template file stationed in package-templates/
- During the packaging process, if a template file exists and its path is passed to the "pack" function (possibly from the config), the bootstrap script will be created and attached to the package (whether by copying it into the package (in case of a tar for instance), or by attaching it (deb, rpm...).)
- The bootstrap script will run automatically upon dpkg-ing when applicable.

Here's an example of a template bootstrap script (for virtualenv, since riemann doesn't require one)::

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

Config Templates:

- it is possible to generate configuration file/s from templates or just copy existing configuration files into the package which can later be used by the bootstrap script to deploy the package along with its config.
- the component's "config_templates" sub-dict can be used for that purpose. 4 types of config template keys exist in the sub-dict:
    - __template_dir - a directory from which template files are generated (iterated over...)
    - __template_file - an explicit name from which a template file is generated.
    - __config_dir - a directory from which config files are copied.
    - __config_file - an explicit name of a config file to be copied.
