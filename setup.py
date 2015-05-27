"""
"""

import os
from setuptools import setup


project_dir = os.path.dirname(__file__)


def read(rel_path):
    return open(
        os.path.join(project_dir, rel_path)
    ).read()


def read_requirements():
    return [
        p.strip() for p in read(
            "requirements.txt"
        ).split("\n") if p.strip()
    ]


setup(
    name="nit",
    version="0.1.0",
    author="Brian Jorgensen",
    author_email="brian.jorgensen+nit@gmail.com",
    description=("A framework for experimenting with "
                 "Git-like versioned storage systems."),
    long_description=read('README.md'),
    install_requires=read_requirements(),
    license = "BSD",
    keywords = "vcs dvcs git",
    url = "",
    packages=['nit'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    scripts=[
        "bin/nit",
        "bin/nit-git"
    ]
)
