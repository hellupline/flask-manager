from codecs import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='flask-manager',
    version='0.0.1alpha',
    description='A CRUD manager for Flask',
    long_description=long_description,
    author='Renan Traba',
    author_email='hellupline@gmail.com',
    url='https://github.com/hellupline/flask-crud',
    download_url='https://github.com/hellupline/flask-manager/tarball/0.0.1',
    keywords=['flask', 'crud', 'sqlalchemy', 'admin', 'manager'],

    license='LGPL3',
    classifiers=[
        ('License :: OSI Approved :: '
         'GNU Lesser General Public License v3 or later (LGPLv3+)'),
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'flask>=0.10',
        'wtforms',
        'wtforms-alchemy',
        'cached-property',
    ],
    extras_require={
        'dev': ['ipython'],
        'test': ['coverage'],
    },
    zip_safe=False,
    include_package_data=True,
)
