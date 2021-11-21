from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os
import sys


def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'textile/version.py')) as f:
        variables = {}
        exec(f.read(), variables)
        return variables.get('VERSION')
    raise RuntimeError('No version info found.')

setup(
    name='textile',
    version=get_version(),
    author='Dennis Burke',
    author_email='ikirudennis@gmail.com',
    description='Textile processing for python.',
    url='http://github.com/textile/python-textile',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='textile,text,html markup',
    install_requires=[
        'html5lib>=1.0.1',
        'regex>1.0; implementation_name != "pypy"',
        ],
    extras_require={
        'develop': ['pytest', 'pytest-cov'],
        'imagesize': ['Pillow>=3.0.0'],
    },
    entry_points={'console_scripts': ['pytextile=textile.__main__:main']},
    tests_require=['pytest', 'pytest-cov'],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.5',
)
