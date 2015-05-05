.DELETE_ON_ERROR:

all:
	echo >&2 "Must specify target."

venv:
	tox -evenv

test:
	tox

clean:
	rm -rf build/ dist/ *.egg-info/ .tox/ venv-*/
	rm -f .coverage
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

.PHONY: all test clean
