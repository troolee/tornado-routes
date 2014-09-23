# -*- coding: utf-8 -*-
#
# Author: Pavel Reznikov <pashka.reznikov@gmail.com>
# Created: 23/01/13
#
# Id: $Id$

"""`tornado-routes` lives on `GitHub <https://github.com/troolee/tornado-routes>`_."""
from setuptools import setup


setup(
    name="tornado-routes",
    version="0.0.3",
    author="Pavel Reznikov",
    author_email="pashka.reznikov@gmail.com",
    description="URL routings for tornado web server",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    license="MIT",
    keywords="routes tornado tornadoweb routings",
    url="https://github.com/troolee/tornado-routes",
    py_modules=['tornado_routes'],
    long_description=__doc__,
    install_requires=['tornado', 'six'],
)
