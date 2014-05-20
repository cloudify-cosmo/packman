.PHONY: release update docs test

release: test docs update

update:
	grep '# TODO' -rn * --exclude-dir=docs --exclude-dir=build --exclude=TODO.md | sed 's/: \+#/:    # /g;s/:#/:    # /g' | sed -e 's/^/- /' | grep -v Makefile > TODO.md
	git log --oneline --decorate --color > CHANGELOG

docs:
	cd docs && make html
	pandoc README.md -f markdown -t rst -s -o README.rst

test:
	tox

# TODO: (optional) - add install task to makefile