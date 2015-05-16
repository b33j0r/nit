#! /usr/bin/env python
"""
"""
from unittest import TestCase
from pathlib import Path
from collections import namedtuple

from nit.core.status import BaseStatusStrategy


MockNode = namedtuple("MockNode", ("path", "key"))

a1 = MockNode(Path("a"), "aaaa1")
a2 = MockNode(Path("a"), "aaaa2")

b1 = MockNode(Path("b"), "bbbb1")
b2 = MockNode(Path("b"), "bbbb2")

c1 = MockNode(Path("c"), "cccc1")
c2 = MockNode(Path("c"), "cccc2")

d1 = MockNode(Path("d"), "dddd1")
d2 = MockNode(Path("d"), "dddd2")

e1 = MockNode(Path("e"), "eeee1")
e2 = MockNode(Path("e"), "eeee2")

f1 = MockNode(Path("f"), "ffff1")
f2 = MockNode(Path("f"), "ffff2")


class BaseTreeDiffTests(TestCase):

    """
    """

    def setUp(self):
        head_tree = [
            a1, b1, c1
        ]
        index_tree = [
            a1, b2, d1
        ]
        working_tree = [
            a1, b2, d1, e1, f1
        ]

        self.diff = BaseStatusStrategy(
            head_tree,
            index_tree,
            working_tree,
            ignorer=lambda n: str(n).startswith("f")
        )

    def test_unmodified(self):
        assert {a1} == self.diff.unmodified

    def test_modified(self):
        assert {b2} == self.diff.modified

    def test_removed(self):
        assert {c1} == self.diff.removed

    def test_added(self):
        assert {d1} == self.diff.added

    def test_untracked(self):
        assert {e1} == self.diff.untracked

    def test_ignored(self):
        assert {f1} == self.diff.ignored


class BaseTreeDiffNoHeadTests(TestCase):

    """
    """

    def setUp(self):
        head_tree = None
        index_tree = [
            a1, b2, d1
        ]
        working_tree = [
            a1, b2, d1, e1, f1
        ]

        self.diff = BaseStatusStrategy(
            head_tree,
            index_tree,
            working_tree,
            ignorer=lambda n: str(n).startswith("f")
        )

    def test_unmodified(self):
        assert set() == self.diff.unmodified

    def test_modified(self):
        assert set() == self.diff.modified

    def test_removed(self):
        assert set() == self.diff.removed

    def test_added(self):
        assert {a1, b2, d1} == self.diff.added

    def test_untracked(self):
        assert {e1} == self.diff.untracked

    def test_ignored(self):
        assert {f1} == self.diff.ignored
