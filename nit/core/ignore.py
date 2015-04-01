#! /usr/bin/env python
"""
"""
import os


class IgnoreStrategy:
    """
    """

    def should_ignore(self, file_path):
        always_ignore = [".nit"]
        path_components = file_path.split(os.pathsep)
        return any(c in always_ignore for c in path_components)
