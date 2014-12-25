#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name             = 'kindlereader',
    version          = '0.0.2',
    description      = 'generate news for kindle reader from rss',
    long_description = open('README').read(),

    author           = 'Zigler Zhang<zigler.zhang@gmail.com>',
    author_email     = 'zigler.zhang@gmail.com',
    url              = 'https://github.com/fireinice/kindlereader2',
    license          = open("LICENSE").read(),

    install_requires = ['yakindlestrip>=1.35',
                        'librssreader>=0.0.5',
                        'tornado>=3.0',
                        'pytz >= 2014.9',
                        'BeautifulSoup >= 3.2.1',
                        'python-gflags>=2.0'],

    packages         = ['krlib'],
    scripts         = ['kindlereader.py'],
    test_suite       = 'tests',
    #https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers      = (
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: General',
        'Topic :: Internet :: WWW/HTTP',
    ),
)
