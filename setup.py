#!/usr/bin/python

from setuptools import setup
from setuptools import find_packages

__module__ = 'netconfig'
__url__ = 'https://github.com/ccxtechnologies'

__version__ = None
exec(open(f'{__module__}/__version__.py').read())

setup(
        name=__module__,
        version=__version__,
        author='CCX Technologies',
        author_email='charles@ccxtechnologies.com',
        description='Linux network configuration tools',
        long_description=open('README.rst', 'rt').read(),
        license='MIT',
        url=f'{__url__}/{__module__}',
        download_url=f'{__url__}/archive/v{__version__}.tar.gz',
        python_requires='>=3.7',
        packages=find_packages(),
)
