#!/usr/bin/env python

from distutils.core import setup

setup(name='gccinvocation',
    version='0.1',
    description='Library for parsing GCC command-line options',
    py_modules = ['gccinvocation'],
    license='LGPLv2.1+',
    author='David Malcolm <dmalcolm@redhat.com>',
    url='https://github.com/fedora-static-analysis/gccinvocation',
    classifiers=(
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    )
)
