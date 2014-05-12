=============================
Components File Configuration
=============================

Configuration of all components is done via a python file containing a single dict with multiple (per component) sub-dicts.
We will call it the "components file".

A Component's Structure
-----------------------
A component is comprised of a set of key:value pairs.
Each component has a set of mandatory parameters like name and version and of optional parameters like source_urls.
Obviously, after processing, a component becomes a package...

A very simple example of a component's configuration for riemann::

    COMPONENTS_PACKAGES_PATH = '/TEST'
    PACKAGES_PATH = '/TEST2'
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

The Configuration Parameters
----------------------------
By default, a component can be comprised of a set of parameters, all of which (names) are configurable in the definitions.py file (This is currently only available by editing the module directly). The file is not currently directly available to the user (as most of the parameters names are self-explanatory) but at a future version, a user will be able to override the parameter names by supplying an overriding definitions.py file (to override all or some of the parameter names).

TODO: ADD A LINK TO THE DEFINITIONS FILE.