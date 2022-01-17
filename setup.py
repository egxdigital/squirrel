"""Squirrel Setup

This module contains the setuptools.setup() definition for the Squirrel program.

Usage
    pip freeze > requirements.txt \\
    deactivate \\
    sudo python3.9 -m setup develop
"""
import os
from pathlib import Path, PurePath
from setuptools import setup, find_packages

root = Path(__file__).resolve().parent
requirements_txt = Path(PurePath(root, 'requirements.txt'))


def read_requirements_file(fd):
    res = []
    if Path(fd).is_file():
        with open(fd, 'r') as reader:
            reqs = [lin.strip('\n')
                    for lin in reader.readlines() if '#' not in lin]
            res += [req for req in reqs if os.getenv(
                'python', '/home/engineer/source/python/projects') not in req]
    return res


with open('README.md', 'r') as fh:
    long_description = fh.read()

requirements = read_requirements_file(requirements_txt)

setup(
    name='Squirrel',
    version='1.0.0',
    author='Emille Giddings',
    author_email='emilledigital@gmail.com',
    description='<enter description here>',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    install_requires=requirements,
    packages=find_packages(include=['']),
    package_data={'': ['', '']},
    entry_points={
        'console_scripts': ['squirrel=squirrel.__main__:main']
    },
    tests_require=[''],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9'
)
