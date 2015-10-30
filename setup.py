#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


__title__ = 'futgui'
__version__ = '0.0.1'
__author__ = 'Jason Hunter'
__author_email__ = 'hunterjm@gmail.com'
__license__ = 'GNU GPL v3'
__copyright__ = 'Copyright 2015 Jason Hunter'

packages = [
    __title__,
    '%s.core' % __title__,
    '%s.dmg' % __title__,
    '%s.fonts' % __title__,
    '%s.frames' % __title__,
    '%s.images' % __title__,
]


with open('requirements.txt') as f:
    requires = [i for i in f.read().splitlines() if i[:8] != 'https://']

with open('readme.md') as f1:
    long_desc = f1.read()

setup(
    name=__title__,
    version=__version__,
    description=__title__,
    long_description=long_desc,
    author=__author__,
    author_email=__author_email__,
    url='https://github.com/hunterjm/%s' % __title__,
    download_url='https://github.com/hunterjm/%s/releases' % __title__,
    bugtrack_url='https://github.com/hunterjm/%s/issues' % __title__,
    platforms='any',
    keywords=__title__,
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={__title__: __title__},
    include_package_data=True,
    install_requires=requires,
    # license=open('LICENSE').read(),
    license=__license__,
    classifiers=(
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.0',  # not tested
        # 'Programming Language :: Python :: 3.1',  # not tested
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',  # not tested
        # 'Programming Language :: Python :: Implementation :: CPython',  # not tested
        # 'Programming Language :: Python :: Implementation :: IronPython',  # not tested
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
