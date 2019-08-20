#!/usr/bin/env python3

# python setup.py sdist --format=zip,gztar

import os
import sys
import platform
import importlib.util
import argparse
import subprocess

from setuptools import setup, find_packages
from setuptools.command.install import install

MIN_PYTHON_VERSION = "3.6.1"
_min_python_version_tuple = tuple(map(int, (MIN_PYTHON_VERSION.split("."))))


if sys.version_info[:3] < _min_python_version_tuple:
    sys.exit("Error: Zephyr requires Python version >= %s..." % MIN_PYTHON_VERSION)

with open('contrib/requirements/requirements.txt') as f:
    requirements = f.read().splitlines()

with open('contrib/requirements/requirements-hw.txt') as f:
    requirements_hw = f.read().splitlines()

# load version.py; needlessly complicated alternative to "imp.load_source":
version_spec = importlib.util.spec_from_file_location('version', 'zephyr_code/version.py')
version_module = version = importlib.util.module_from_spec(version_spec)
version_spec.loader.exec_module(version_module)

data_files = []

if platform.system() in ['Linux', 'FreeBSD', 'DragonFly']:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root=', dest='root_path', metavar='dir', default='/')
    opts, _ = parser.parse_known_args(sys.argv[1:])
    usr_share = os.path.join(sys.prefix, "share")
    icons_dirname = 'pixmaps'
    if not os.access(opts.root_path + usr_share, os.W_OK) and \
       not os.access(opts.root_path, os.W_OK):
        icons_dirname = 'icons'
        if 'XDG_DATA_HOME' in os.environ.keys():
            usr_share = os.environ['XDG_DATA_HOME']
        else:
            usr_share = os.path.expanduser('~/.local/share')
    data_files += [
        (os.path.join(usr_share, 'applications/'), ['zephyr.desktop']),
        (os.path.join(usr_share, icons_dirname), ['zephyr_code/gui/icons/zephyr.png']),
    ]

extras_require = {
    'hardware': requirements_hw,
    'fast': ['pycryptodomex'],
    'gui': ['pyqt5'],
}
extras_require['full'] = [pkg for sublist in list(extras_require.values()) for pkg in sublist]


setup(
    name="Zephyr",
    version=version.ELECTRUM_VERSION,
    python_requires='>={}'.format(MIN_PYTHON_VERSION),
    install_requires=requirements,
    extras_require=extras_require,
    packages=[
        'zephyr_code',
        'zephyr_code.gui',
        'zephyr_code.gui.qt',
        'zephyr_code.plugins',
    ] + [('zephyr_code.plugins.'+pkg) for pkg in find_packages('zephyr_code/plugins')],
    package_dir={
        'zephyr': 'zephyr'
    },
    package_data={
        '': ['*.txt', '*.json', '*.ttf', '*.otf'],
        'zephyr_code': [
            'wordlist/*.txt',
            'locale/*/LC_MESSAGES/electrum.mo',
        ],
        'zephyr_code.gui': [
            'icons/*.*',
            'icons/radio/*.*',
            'icons/checkbox/*.*',
        ],
    },
    scripts=['zephyr_code/zephyr'],
    data_files=data_files,
    description="Lightweight PIVX Wallet",
    maintainer="Cryptosi",
    maintainer_email="cryptosi@protonmail.com",
    license="MIT License",
    url="https://github.com/mrcarlanthony/Zephyr-wallet",
    long_description="""Lightweight PIVX Wallet""",
)
