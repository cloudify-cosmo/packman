# flake8: NOQA
from user_definitions import *

PACKAGES = {
	 "trio": {
        "name": "trio",
     		"version": "1",
     	 	"package_path": "{0}/trio/".format(PACKAGES_PATH),
      	"sources_path": "{0}/trio".format(SOURCES_PATH),
      	"src_package_type": "dir",
      	"dst_package_type": "deb",
      	"reqs": [
            {
                "url": "https://github.com/nir0s/packman-example/archive/develop.tar.gz",
                "components": ['kibana3'],
            },
        ]
    },
}
