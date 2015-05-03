# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

__version__ = '1.1.1'


setup(
    name='combine',
    version=__version__,
    provides=['combine'],
    author='MLSec Project',
    url='https://github.com/mlsecproject/combine',
    setup_requires='setuptools',
    license='GPLv3',
    description='Combine gathers Threat Intelligence from publicly available sources',
    packages=find_packages(),
    install_requires=[
        'CsvSchema==1.1.1',
        'argparse>=1.2.1,<1.4.0',
        'beautifulsoup4==4.3.2',
        'feedparser==5.1.3',
        'gevent==1.0.1',
        'greenlet>=0.4.2,<0.5.0',
        'netaddr==0.7.12',
        'pygeoip>=0.3.1,<0.4.0',
        'requests>=2.3.0,<2.6.0',
        'sortedcontainers==0.9.4',
        'wsgiref==0.1.2',
        'unicodecsv==0.9.4',
    ],
    dependency_links=[
        "git+https://github.com/rtdean/grequests@19239a34b00b8ac226b21f01b0fb55e869097fb7#egg=grequests-0.3.1"
    ],
    entry_points={
        'console_scripts': [
            'combine=combine.combine:main',
            'reaper=combine.reaper:main',
            'thresher=combine.thresher:main',
            'winnower=combine.winnower:main',
            'baler=combine.baler:main',
        ],
    },
)
