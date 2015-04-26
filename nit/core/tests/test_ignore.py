#! /usr/bin/env python
"""
"""
import os
from unittest import TestCase
from nit.core.ignore import (
    RelativeIgnorePredicate,
    RegexIgnorePredicate,
    PathspecIgnorePredicate,
    CompoundIgnorePredicate
)


class RelativeIgnorePredicateTests(TestCase):

    """
    """

    class DummyPredicate(RelativeIgnorePredicate):
        def ignore_relative_path(self, relative_file_path):
            return "ignore" in str(relative_file_path)

    def setUp(self):
        self.predicate = self.DummyPredicate()

    def test_not_relative(self):
        assert self.predicate.ignore(
            "/fake", "/notfake"
        )

    def test_relative_ignore(self):
        assert self.predicate.ignore(
            "/fake", "/fake/ignore"
        )

    def test_relative_included(self):
        assert not self.predicate.ignore(
            "/fake", "/fake/include"
        )


class RegexIgnorePredicateTests(TestCase):

    """
    """

    def setUp(self):
        self.predicate = RegexIgnorePredicate(
            r"ignore([^d]|$)"
        )

    def test_not_relative(self):
        assert self.predicate.ignore(
            "/fake", "/notfake"
        )

    def test_relative_ignore(self):
        assert self.predicate.ignore(
            "/fake", "/fake/ignore"
        )

    def test_relative_included(self):
        assert not self.predicate.ignore(
            "/fake", "/fake/include"
        )

    def test_relative_included_regex(self):
        assert not self.predicate.ignore(
            "/fake", "/fake/ignored"
        )

    def test_relative_ignored_regex(self):
        assert self.predicate.ignore(
            "/fake", "/fake/ignores"
        )


class PathspecIgnorePredicateTests(TestCase):

    sep = "/"

    @classmethod
    def setUp(self):
        self.original_sep = os.path.sep
        os.path.sep = self.sep

    @classmethod
    def tearDown(self):
        os.path.sep = self.original_sep

    def test_dot(self):
        predicate = PathspecIgnorePredicate(
            ".ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + ".ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "cignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignore"
        )

    def test_negate(self):
        predicate = PathspecIgnorePredicate(
            "!.ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + ".ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "cignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignore"
        )

    def test_leading_slash(self):
        predicate = PathspecIgnorePredicate(
            os.path.sep + "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "ignore"
        )

    def test_no_leading_slash(self):
        predicate = PathspecIgnorePredicate(
            "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "include"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "include"
        )

    def test_single_wildcard(self):
        predicate = PathspecIgnorePredicate(
            "ignore?"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignored"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "ignored"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "ignore"
        )

    def test_multi_wildcard(self):
        predicate = PathspecIgnorePredicate(
            "ignore*"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignored"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "ignored"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignor"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "ignor"
        )

    def test_leading_double_wildcard(self):
        predicate = PathspecIgnorePredicate(
            "**/ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "subsubdir" + os.path.sep + "ignore"
        )

    def test_double_wildcard(self):
        predicate = PathspecIgnorePredicate(
            "subdir/**/ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "foo" + os.path.sep + "ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "foo" + os.path.sep + "subdir" + os.path.sep + "subsubdir" + os.path.sep + "ignore"
        )

    def test_char_class(self):
        predicate = PathspecIgnorePredicate(
            "[ab]/ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "a" + os.path.sep + "ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "c" + os.path.sep + "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "c" + os.path.sep + "b" + os.path.sep + "ignore"
        )

    def test_negated_char_class(self):
        predicate = PathspecIgnorePredicate(
            "![ab]/ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "a" + os.path.sep + "ignore"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "c" + os.path.sep + "ignore"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "c" + os.path.sep + "b" + os.path.sep + "ignore"
        )

    def test_trailing_slash(self):
        predicate = PathspecIgnorePredicate(
            "subdir/"
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep
        )
        assert predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdir" + os.path.sep + "a"
        )
        assert not predicate.ignore(
            os.path.sep + "fake",
            os.path.sep + "fake" + os.path.sep + "subdira"
        )


class CompoundIgnorePredicateTests(TestCase):

    """
    """

    def setUp(self):
        self.predicate = CompoundIgnorePredicate([
            PathspecIgnorePredicate(".ignore"),
            PathspecIgnorePredicate("*.py[cd]"),
        ])

    def test_test_ignored(self):
        assert self.predicate.ignore(
            "/fake",
            "/fake/.ignore"
        )
        assert self.predicate.ignore(
            "/fake",
            "/fake/thing.pyc"
        )
        assert self.predicate.ignore(
            "/fake",
            "/fake/subdir/thing.pyc"
        )

    def test_test_included(self):
        assert not self.predicate.ignore(
            "/fake",
            "/fake/ignore"
        )
        assert not self.predicate.ignore(
            "/fake",
            "/fake/thing.py"
        )
        assert not self.predicate.ignore(
            "/fake",
            "/fake/subdir/thing.py"
        )
        assert not self.predicate.ignore(
            "/fake",
            "/fake/subdir/ignore"
        )


# class WindowsPathspecIgnorePredicateTests(PathspecIgnorePredicateTests):
#
#     sep = "\\"
