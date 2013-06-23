import os
import sys
from setuptools import setup, find_packages

# Hack to silence atexit traceback in newer python versions
try:
    import multiprocessing  # NOQA
except ImportError:
    pass

DESCRIPTION = 'MotorEngine is a port of the amazing MongoEngine Mapper using non-blocking I/O.'
LONG_DESCRIPTION = 'MotorEngine is a port of the amazing MongoEngine Mapper using non-blocking I/O.'


def get_version(version_tuple):
    if not isinstance(version_tuple[-1], int):
        return '.'.join(map(str, version_tuple[:-1])) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))

# Dirty hack to get version number from monogengine/__init__.py - we can't
# import it as it depends on PyMongo and PyMongo isn't installed until this
# file is read
init = os.path.join(os.path.dirname(__file__), 'motorengine', '__init__.py')
version_line = list(filter(lambda l: l.startswith('VERSION'), open(init)))[0]

VERSION = get_version(eval(version_line.split('=')[-1]))
print(VERSION)

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.1",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: Implementation :: CPython",
    'Topic :: Database',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

extra_opts = {}
extra_opts['packages'] = find_packages(exclude=('tests',))
if sys.version_info[0] == 3:
    extra_opts['use_2to3'] = True
    extra_opts['tests_require'] = ['nose', 'coverage', 'blinker', 'jinja2==2.6', 'rednose']

    if "test" in sys.argv or "nosetests" in sys.argv:
        extra_opts['packages'].append("tests")
        extra_opts['package_data'] = {"tests": ["fields/motorengine.png", "fields/mongodb_leaf.png"]}
else:
    extra_opts['tests_require'] = ['nose', 'coverage', 'blinker', 'django>=1.4.2', 'PIL', 'jinja2==2.6', 'python-dateutil', 'rednose']

setup(
    name='motorengine',
    version=VERSION,
    author='TDispatch',
    author_email='dev@tdispatch.com',
    maintainer="Bernardo Heynemann",
    maintainer_email="heynemann@tdispatch.com",
    url='https://github.com/TDispatch/motorengine/',
    download_url='https://github.com/TDispatch/motorengine/tarball/master',
    license='MIT',
    include_package_data=True,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'six',
        'motor',
        'tornado'
    ],
    extras_require={
        'tests': extra_opts['tests_require']
    },
    test_suite='nose.collector',
    **extra_opts
)
