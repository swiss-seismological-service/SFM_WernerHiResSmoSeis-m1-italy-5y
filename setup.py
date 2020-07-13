# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
setup.py for ramsis.sfm.em1

.. note:

    Packaging is performed by means of `Python namespace packages
    <https://packaging.python.org/guides/packaging-namespace-packages/>`_
"""

import os
import sys
from setuptools import setup


if sys.version_info[:2] < (3, 6):
    raise RuntimeError("Python version >= 3.6 required.")


def get_version(filename):
    from re import findall
    with open(filename) as f:
        metadata = dict(findall("__([a-z]+)__ = '([^']+)'", f.read()))
    return metadata['version']

# get_version ()


_authors = [
    'Lukas Heiniger',
    'Daniel Armbruster']
_authors_email = [
    'lukas.heiniger@sed.ethz.ch',
    'daniel.armbruster@sed.ethz.ch']

_install_requires = [
    'numpy==1.15',
    'obspy==1.1.0',
    "ramsis.sfm.worker==0.1",
    "GeoAlchemy2==0.6.3",
    "pandas==0.25.0",
    "Flask==1.1.1",
    "Flask-RESTful==0.3.7",
    "Flask-SQLAlchemy==2.4.0",
    "scipy==1.3.0",
    "webargs>=5.3.2",
    "GDAL==2.2.3",
    "ramsis.utils==0.1",
    "pyproj", ]

_extras_require = {'doc': [
    "sphinx==1.4.1",
    "sphinx-rtd-theme==0.1.9", ],
    "postgres": ["psycopg2==2.8.3"]}

_tests_require = []

_data_files = [
    ('', ['LICENSE'])]

_entry_points = {
    'console_scripts': [
        'ramsis-sfm-worker-em1 = ramsis.sfm.em1.server.app:main', ]}

_name = 'ramsis.sfm.em1'
_version = get_version(os.path.join('ramsis', 'sfm', 'em1', '__init__.py'))
_description = ('RT-RAMSIS SFM-Worker (EM1).')
_packages = ['ramsis.sfm.em1',
             'ramsis.sfm.em1.server',
             'ramsis.sfm.em1.server.v1',
             'ramsis.sfm.em1.core', ]
_namespace_packages = ['ramsis', 'ramsis.sfm']

# ----------------------------------------------------------------------------
setup(
    name=_name,
    # TODO(damb): Provide version string globally
    version=_version,
    author=' (SED, ETHZ),'.join(_authors),
    author_email=', '.join(_authors_email),
    description=_description,
    license='AGPL',
    keywords=[
        'induced seismicity',
        'risk',
        'risk assessment',
        'risk mitigation',
        'realtime',
        'seismology'],
    url='https://gitlab.seismo.ethz.ch/indu/ramsis.worker.git',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Science/Research',
        ('License :: OSI Approved :: GNU Affero '
            'General Public License v3 or later (AGPLv3+)'),
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering', ],
    platforms=['Linux', ],
    packages=_packages,
    namespace_packages=_namespace_packages,
    data_files=_data_files,
    install_requires=_install_requires,
    extras_require=_extras_require,
    tests_require=_tests_require,
    include_package_data=True,
    zip_safe=False,
    entry_points=_entry_points
)
