#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'psycopg2==2.6.1',
    'emails==0.5.4',
    'sopel==6.1.1',
    'EasySettings==2.0.4',
    'SQLAlchemy==1.0.10',
]

test_requirements = [
    'pytest',
]

setup(
    name='bulletbot',
    version='0.1.0',
    description="Chat bot for logging employee completed tasks.",
    long_description=readme + '\n\n' + history,
    author="Joshua Miller",
    author_email='jsmiller@uchicago.edu',
    url='https://github.com/millerjs/bulletbot',
    packages=['bulletbot'],
    package_dir={'bulletbot': 'bulletbot'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='bulletbot',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
