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
        return self.ignore_path(base_path, file_path)

    @abstractmethod
    def ignore_path(self, base_path, file_path):
        """
        Returns True if `file_path` should be ignored.
        """
        pass


class CompoundIgnorePredicate(IgnorePredicate):

    """
    Wraps a list of IgnorePredicate instances
    and tests all of them when ignore() is
    called.
    """

    def __init__(self, predicates=None):
        self.predicates = list(predicates) or []

    def ignore_path(self, base_path, file_path):
        """
        """
        return any(
            p.ignore_path(base_path, file_path)
            for p in self.predicates
        )


class RelativeIgnorePredicate(IgnorePredicate):

    """
    Base class for the most common scenario,
    only testing for ignore patterns within
    the base project directory.
    """

    def ignore_path(self, base_path, file_path):
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

        return self.ignore_relative_path(
            relative_file_path
        )

    @abstractmethod
    def ignore_relative_path(self, relative_file_path):
        pass


class RegexIgnorePredicate(RelativeIgnorePredicate):

    """
    An ignore predicate that ignores a relative
    file path when the given regex pattern is matched.
    """

    def __init__(self, pattern):
        self.regex = re.compile(pattern)

    def ignore_relative_path(self, relative_file_path):
        return self.regex.search(
            str(relative_file_path)
        ) is not None


class PathspecIgnorePredicate(RegexIgnorePredicate):

    def __init__(self, pattern):
        self.is_negated = False
        self.is_rooted = False
        self.is_parent = False
        pattern = str(pattern)
        pattern = self._build_pattern(pattern)
        super().__init__(pattern)

    def ignore_path(self, base_path, file_path):
        ignore = super().ignore_path(base_path, file_path)
        return (not ignore) if self.is_negated else ignore

    def _build_pattern(self, pattern):
        pattern = pattern.strip()

        if pattern.startswith("!"):
            self.is_negated = True
            pattern = pattern[1:]

        if pattern.startswith("/"):
            self.is_rooted = True
            pattern = pattern[1:]

        if pattern.endswith("/"):
            self.is_parent = True
            pattern = pattern[:-1]

        pattern_segs = pattern.split("/")

        pattern_segs = [
            self._escape(p) for p in pattern_segs
        ]

        return (
            ("^" if self.is_rooted else "") +
            os.path.sep.join(pattern_segs) +
            (
                "$" if not self.is_parent else
                "(" + os.path.sep + ".*|$)"
            )
        )

    @staticmethod
    def _escape(pattern):
        pattern = pattern.replace(".", r"\.")
        pattern = pattern.replace("?", ".")
        pattern = pattern.replace("**", ".+")
        pattern = pattern.replace("*", ".*")
        return pattern


class DirPathspecIgnorePredicate(PathspecIgnorePredicate):

    """
    """
