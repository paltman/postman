import os
from setuptools import setup, find_packages

from postman import __version__


def read(*path):
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *path)).read()


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
    install_requires = [
        "argparse==1.2.1",
        "boto>=2.0"
    ]
)
