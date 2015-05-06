"""
Tools for checking the validity of top-level domains, either
in an online (Internet connected) mode, or by caching a set of
known good TLDs and checking offline.
"""

import sys
from setuptools import setup, find_packages

def main():

	python_version = sys.version_info[:2]
	python_3 = sys.version_info[0] == 3

	if python_3:
		raise SystemExit("Sorry, Python 2.x only")
	if python_version < (2,5):
		raise SystemExit("Sorry, Python 2.5 or newer required")

	from uniaccept import __version__

	arguments = {
		'name': 'uniaccept',
		'packages': find_packages(),
		'provides': ['uniaccept'],
		'version': __version__,
		
		'description': 'Universal Acceptance of Domains',
		'long_description': __doc__,
		'author': 'Kim Davies',
		'author_email': 'kim.davies@icann.org',
		'license': 'BSD-like',
		'url': 'https://github.com/icann/uniaccept-python',
		'classifiers': [
			'Development Status :: 3 - Alpha',
			'Intended Audience :: Developers',
			'Intended Audience :: System Administrators',
			'License :: OSI Approved :: BSD License',
			'Operating System :: OS Independent',
			'Topic :: Internet :: Name Service (DNS)',
			'Topic :: Software Development :: Libraries :: Python Modules',
			'Topic :: Utilities',
		],
	}
	
	setup(**arguments)

if __name__ == '__main__':
	main()
