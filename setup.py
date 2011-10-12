import os
import sys
from setuptools import setup, find_packages

from postman import __version__


def read(*path):
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *path)).read()

pyversion = sys.version_info[:2]
install_requires = ["boto>=2.0"]
if pyversion < (2,7) or (3,0) <= pyversion <= (3,1):
    install_requires.append('argparse')

setup(
    name = "postman",
    version = __version__,
    description = "Command line for Amazon SES",
    long_description=read("README.rst"),
    author = "Patrick Altman",
    author_email = "paltman@gmail.com",
    packages = find_packages(),
    zip_safe = False,
    entry_points = {
        "console_scripts": [
            "postman = postman.__main__:main",
        ],
    },
    install_requires = install_requires,
)
