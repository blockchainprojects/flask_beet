# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="Flask-Beet",
    version="0.1",
    url="http://bitshares.eu/",
    license="MIT",
    author="Fabian Schuh",
    author_email="fabian@chainsquad.com",
    description="A flask extension that allows login via Beet app",
    long_description=open("README.md").read(),
    packages=["flask_beet"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[open("requirements.txt").readlines()],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
