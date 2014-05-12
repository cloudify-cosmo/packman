# flake8: NOQA
########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from user_definitions import *

PACKAGES = {
    "openjdk-7-jdk": {
        "name": "openjdk-7-jdk",
        "version": "0.0.1",
        "reqs": [
            "openjdk-7-jdk"
        ],
        "package_path": "{0}/openjdk-7-jdk/".format(PACKAGES_PATH),
        "sources_path": "{0}/openjdk-7-jdk".format(SOURCES_PATH),
        "dst_package_type": "deb",
    },
    "logstash": {
        # a component's name
        "name": "logstash",
        # a component's version
        "version": "1.3.2",
        # a list of source urls to download
        "source_urls": [
            "https://download.elasticsearch.org/logstash/logstash/logstash-1.3.2-flatjar.jar",
        ],
        # a list of dependencies (for deb, rpm, etc..)
        "depends": [
            'openjdk-7-jdk'
        ],
        # a package's path - this is where a package will eventually reside after being packed.
        "package_path": "{0}/logstash/".format(PACKAGES_PATH),
        # a package's sources path - this is where all sources will reside before packaging occures.
        "sources_path": "{0}/logstash".format(SOURCES_PATH),
        # the source type to create the package from (according to fpm).
        "src_package_type": "dir",
        # the destination package type to create.
        "dst_package_type": "deb",
        # a bootstrap script to attach to the package.
        "bootstrap_script": "{0}/logstash-bootstrap.sh".format(SCRIPTS_PATH),
        # a bootstrap template name to generate the above script from
        "bootstrap_template": "logstash-bootstrap.template",
        # a sub-dict of configuration file templates.
        "config_templates": {
            # __template_file means a config file will be generated from a single template.
            "__template_file_init": {
                # path to the template file
                "template": "{0}/logstash/init/logstash.conf.template".format(CONFIGS_PATH),
                # output file name
                "output_file": "logstash.conf",
                # output file dir (will be created if doesn't exist)
                "config_dir": "config/init",
                # helper (not mandatory) param which specifies where the file should reside after package installation
                "dst_dir": "/etc/init",
            },
            # helper (not mandatory) subdict for the above template to use.
            "__params_init": {
                "jar": "logstash.jar",
                "log_file": "/var/log/logstash.out",
                "conf_path": "/etc/logstash.conf",
                "run_dir": "/opt/logstash",
                "user": "root",
            },
            "__template_file_conf": {
                "template": "{0}/logstash/conf/logstash.conf.template".format(CONFIGS_PATH),
                "output_file": "logstash.conf",
                "config_dir": "config/conf",
                "dst_dir": "/etc",
            },
            "__params_conf": {
                "events_queue": "cloudify-events",
                "logs_queue": "cloudify-logs",
                "test_tcp_port": "9999",
                "events_index": "cloudify_events",
            }
        }
    },
    "elasticsearch": {
        "name": "elasticsearch",
        "version": "1.0.1",
        "source_urls": [
            "https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.tar.gz",
        ],
        "depends": [
            'openjdk-7-jdk'
        ],
        "package_path": "{0}/elasticsearch/".format(PACKAGES_PATH),
        "sources_path": "{0}/elasticsearch".format(SOURCES_PATH),
        "src_package_type": "dir",
        "dst_package_type": "deb",
        "bootstrap_script": "{0}/elasticsearch-bootstrap.sh".format(SCRIPTS_PATH),
        "bootstrap_template": "elasticsearch-bootstrap.template",
        "config_templates": {
            "__template_file_init": {
                "template": "{0}/elasticsearch/init/elasticsearch.conf.template".format(CONFIGS_PATH),
                "output_file": "elasticsearch.conf",
                "config_dir": "config/init",
                "dst_dir": "/etc/init",
            },
            "__params_init": {
                "run_dir": "/opt/elasticsearch",
                "user": "root",
            },
            "__template_file_conf": {
                "template": "{0}/elasticsearch/init/elasticsearch.conf.template".format(CONFIGS_PATH),
                "output_file": "elasticsearch.conf",
                "config_dir": "config/conf",
                "dst_dir": "/etc/init",
            },
            "__params_conf": {
            }
        }
    },
    "kibana3": {
        "name": "kibana3",
        "version": "3.0.0milestone4",
        "source_urls": [
            "https://download.elasticsearch.org/kibana/kibana/kibana-3.0.0milestone4.tar.gz",
        ],
        "depends": [
            'openjdk-7-jdk',
            'logstash',
            'elasticsearch'
        ],
        "package_path": "{0}/kibana3/".format(PACKAGES_PATH),
        "sources_path": "{0}/kibana3".format(SOURCES_PATH),
        "src_package_type": "dir",
        "dst_package_type": "deb",
        "bootstrap_script": "{0}/kibana-bootstrap.sh".format(SCRIPTS_PATH),
        "bootstrap_template": "kibana-bootstrap.template",
    },
     "ruby": {
        "name": "ruby2.1",
        "version": "2.1.0",
        "depends": [
            'make'
        ],
        "package_path": "{0}/ruby/".format(PACKAGES_PATH),
        "sources_path": "/opt/ruby",
        "src_package_type": "dir",
        "dst_package_type": "deb",
        "ruby_build_dir": "/opt/ruby-build"
    }
}