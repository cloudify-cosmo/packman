# flake8: NOQA

PACKAGES = {
    "mock_component": {
        "sources_path": "tests/resources",
        "test_template_parameter": "test_template_output",
        "config_templates": {
            "__template_file": {
                "template": "tests/templates/mock_template.template",
                "output_file": "mock_template",
                "config_dir": "config/init",
            },
            "__template_dir": {
                "templates": "tests/templates",
                "config_dir": "config/init",
            },
            "__config_dir": {
                "files": "tests/templates",
                "config_dir": "config",
            },
        }
    }
}
