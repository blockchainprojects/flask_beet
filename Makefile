.PHONY: clean-pyc clean-build docs

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr __pycache__/ .eggs/ .cache/ .tox/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	black flask_beet

test:
	pytest

build:
	python3 setup.py build

install: build
	python3 setup.py install

install-user: build
	python3 setup.py install --user

git:
	git push --all
	git push --tags

check:
	twine check dist/*

dist:
	python3 setup.py sdist bdist_wheel
	python3 setup.py bdist_wheel

upload:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

docs:
	sphinx-apidoc -d 6 -e -f -o docs . *.py app
	make -C docs clean html

prepare: clean test docs authors

semver: semver-release semver-updates

semver-release:
	semversioner release

semver-updates:
	semversioner changelog > CHANGELOG.md
	$(eval CURRENT_VERSION = $(shell semversioner current-version))
	sed -i "s/^__version__.*/__version__ = \"$(CURRENT_VERSION)\"/" setup.py
	git add .changes setup.py CHANGELOG.md
	git commit -m "semverioner release updates" --no-verify
	git flow release start $(CURRENT_VERSION)
	git flow release finish $(CURRENT_VERSION)

release: semver clean dist check upload git
