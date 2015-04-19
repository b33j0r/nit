#! /usr/bin/env python
"""
"""
import os
import pathspec
from abc import ABCMeta


class PathspecIgnoreStrategy(metaclass=ABCMeta):

    """
    """

    def __init__(self, root):
        pass

    def should_ignore(self, file_path):
        pass


class IgnoreStrategy:
    """
    """

    def should_ignore(self, file_path):
        always_ignore = [".nit"]
        path_components = file_path.split(os.pathsep)
        return any(c in always_ignore for c in path_components)
