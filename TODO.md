- packman/pkm.py:63:    #  TODO: currently, distrib is checked thruout the code. change it to once.
- packman/pkm.py:74:    #  TODO: implement verbose output
- 
packman/tests/test_packman.py:512:    #  TODO: add apt handler tests
packman/tests/test_packman.py:513:    #  TODO: add yum handler tests (hrm.. how to?)
packman/definitions.py:32:    #  TODO: DEPRACATE!
packman/packman.py:51:    #  TODO: only perform file related actions if file handler is defined
packman/packman.py:231:    #  TODO: remove auto_get param - it is no longer in use
packman/packman.py:303:    #  TODO: add support for installing reqs from urls
packman/packman.py:358:    #  TODO: remove auto_pack param - it is no longer in use
packman/packman.py:375:    #  TODO: identify dst_pkg_type by distro if not specified explicitly.
packman/packman.py:380:    #  TODO: JEEZ... this archives thing is dumb...
packman/packman.py:381:    #  TODO: replace it with a normal destination path
packman/packman.py:418:    #  TODO: handle cases where a bootstrap script is not a template.
packman/packman.py:484:    #  TODO: actually test the package itself.
packman/packman.py:486:    #  TODO: create mock package
packman/packman.py:503:    #  TODO: remove temporary package
packman/packman.py:549:    #  TODO: apply verbosity according to the verbose flag in pkm
packman/packman.py:550:    #  TODO: instead of a verbose flag in the config.
packman/packman.py:637:    #  TODO: handle multiple files differently
packman/packman.py:661:    #  TODO: depracate this useless thing...
packman/packman.py:777:    #  TODO: support virtualenv --relocate OR
packman/packman.py:778:    #  TODO: support whack http://mike.zwobble.org/2013/09/relocatable-python-virtualenvs-using-whack/ # NOQA
packman/packman.py:794:    #  TODO: remove static paths for ruby installations..
packman/packman.py:795:    #  TODO: add support for ruby in different environments
packman/packman.py:861:    #  TODO: add an is-package-installed check. if it is
packman/packman.py:862:    #  TODO: run yum reinstall instead of yum install.
packman/packman.py:864:    #  TODO: yum download exists with an error even if the download
packman/packman.py:865:    #  TODO: succeeded due to a non-zero error message. handle it better.
packman/packman.py:866:    #  TODO: add yum enable-repo option
packman/packman.py:867:    #  TODO: support yum reinstall including dependencies
packman/packman.py:868:    #  TODO: reinstall $(repoquery --requires --recursive --resolve pkg)
packman/packman.py:924:    #  TODO: fix this... (it should dig a bit deeper)
packman/packman.py:959:    #  TODO: add an is-package-installed check. if it is
packman/packman.py:960:    #  TODO: run apt-get install --reinstall instead of apt-get install.
packman/packman.py:1104:    #  TODO: implement?
packman/packman.py:1127:    #  TODO: replace this with method generate_from_template()..
packman/packman.py:1324:    #  TODO: receive PRINT_TEMPLATES from pkm
vagrant/provision.sh:27:    #  TODO: add virtualenv
vagrant/provision.sh:31:    #  TODO: add bash completion support using docopt-completion
