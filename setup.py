from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='flask_crud',
    version='0.1.0',
    description='A Generic CRUD for Flask',
    long_description=long_description,
    url='https://gitlab.com/mucca/le_crud',
    author='Renan Traba',
    author_email='hellupline@gmail.com',
    keywords='flask crud sqlalchemy',

    license='GPL3',
    classifiers=[
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'flask>=0.7',
        'wtforms',
        'wtforms-alchemy'
    ],
    extras_require={
        'dev': ['ipython'],
        'test': ['coverage'],
    },
    include_package_data=True,
)
