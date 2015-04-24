#! /usr/bin/env python
"""
"""
from itertools import chain
import os
from pathlib import Path
import re
import pathspec
from abc import ABCMeta, abstractmethod


class IgnorePredicate(metaclass=ABCMeta):

    """
    Base class for all ignore predicates
    """

    def ignore(self, base_path, file_path):
        """
        Returns True if `file_path` should be ignored.
        """
        base_path = Path(base_path)
        file_path = Path(file_path)
        return self._ignore(base_path, file_path)

    @abstractmethod
    def _ignore(self, base_path, file_path):
        """
        Returns True if `file_path` should be ignored.
        """
        pass

class RelativeIgnorePredicate(IgnorePredicate):

    """
    Base class for the most common scenario,
    only testing for ignore patterns within
    the base project directory.
    """

    def _ignore(self, base_path, file_path):
        """
        Returns True if `file_path` should be ignored.
        """
        base_path = Path(base_path)
        file_path = Path(file_path)
        try:
            relative_file_path = file_path.relative_to(
                base_path
            )
        except ValueError:
            return True

        return self._ignore_relative(
            relative_file_path
        )

    @abstractmethod
    def _ignore_relative(self, relative_file_path):
        pass


class RegexIgnorePredicate(RelativeIgnorePredicate):

    """
    An ignore predicate that ignores a relative
    file path when the given regex pattern is matched.
    """

    def __init__(self, pattern):
        self.regex = re.compile(pattern)

    def _ignore_relative(self, relative_file_path):
        return self.regex.match(
            str(relative_file_path)
        )
