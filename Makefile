VERSION=$(shell grep -m1 version setup.py | cut -d\' -f2)

binary:
	pex . --python=python3 --python-shebang='/usr/bin/env python3' -e tubeup.__main__:main  -o tubeup-$(VERSION)-py2.py3-none-any.pex

publish:
	git tag -a v$(VERSION) -m 'version $(VERSION)'
	git push --tags
	python setup.py register
	python setup.py sdist upload
