# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages
setup(
    name='openstack_project_create',
    version='0.1.0',
    author=u'Vassilis Kanellopoulos',
    author_email='contact@kanellov.com',
    packages=find_packages(),
    url='https://github.com/kanellov/openstack_project_create',
    license='BSD licence, see LICENCE.txt',
    description='Creates user openstack project on first login',
    long_description=open('README.md').read(),
    zip_safe=False,
)
