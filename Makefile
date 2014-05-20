.PHONY: release update docs test

release: test docs update

update:
    # write in line todos to TODO.md
	grep '# TODO' -rn * --exclude-dir=docs --exclude-dir=build --exclude=TODO.md | sed 's/: \+#/:    # /g;s/:#/:    # /g' | sed -e 's/^/- /' | grep -v Makefile > TODO.md
    # write latest commits to CHANGELOG
	git log --oneline --decorate --color > CHANGELOG

docs:
	# update documentation
	cd docs && make html
	# convert to publish in getcloudify
	pandoc README.md -f markdown -t rst -s -o README.rst

test:
	tox

# TODO: (optional) - add install task to makefile