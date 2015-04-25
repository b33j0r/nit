#! /usr/bin/env python
"""
"""
from tempfile import TemporaryDirectory
from unittest import TestCase
from pathlib import Path
from nit.core.ignore import RelativeIgnorePredicate, RegexIgnorePredicate, PathspecIgnorePredicate


class RelativeIgnorePredicateTests(TestCase):

    """
    """

    class DummyPredicate(RelativeIgnorePredicate):
        def _ignore_relative(self, relative_file_path):
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

    def test_dot(self):
        predicate = PathspecIgnorePredicate(
            ".ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/.ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/cignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/ignore"
        )

    def test_negate(self):
        predicate = PathspecIgnorePredicate(
            "!.ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/.ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/cignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/ignore"
        )

    def test_leading_slash(self):
        predicate = PathspecIgnorePredicate(
            "/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/subdir/ignore"
        )

    def test_no_leading_slash(self):
        predicate = PathspecIgnorePredicate(
            "ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/subdir/ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/include"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/subdir/include"
        )

    def test_single_wildcard(self):
        predicate = PathspecIgnorePredicate(
            "ignore?"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/ignored"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/subdir/ignored"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/subdir/ignore"
        )

    def test_multi_wildcard(self):
        predicate = PathspecIgnorePredicate(
            "ignore*"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/subdir/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/ignored"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/subdir/ignored"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/ignor"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/subdir/ignor"
        )

    def test_leading_double_wildcard(self):
        predicate = PathspecIgnorePredicate(
            "**/ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/subdir/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/subdir/subsubdir/ignore"
        )

    def test_double_wildcard(self):
        predicate = PathspecIgnorePredicate(
            "subdir/**/ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/foo/ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/subdir/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/foo/subdir/subsubdir/ignore"
        )

    def test_char_class(self):
        predicate = PathspecIgnorePredicate(
            "[ab]/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/a/ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/c/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/c/b/ignore"
        )

    def test_negated_char_class(self):
        predicate = PathspecIgnorePredicate(
            "![ab]/ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/a/ignore"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/c/ignore"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/c/b/ignore"
        )

    def test_trailing_slash(self):
        predicate = PathspecIgnorePredicate(
            "subdir/"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/subdir/"
        )
        assert predicate.ignore(
            "/fake",
            "/fake/subdir/a"
        )
        assert not predicate.ignore(
            "/fake",
            "/fake/subdira"
        )
