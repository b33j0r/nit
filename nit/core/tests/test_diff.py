#! /usr/bin/env python
"""
"""
from collections import namedtuple
from unittest import TestCase
from pathlib import Path
from nit.core.diff import BaseTreeDiff


MockNode = namedtuple("TreeNode", ("path", "key", "ignore"))

a1 = MockNode(Path("a"), "aaaa1", False)
a2 = MockNode(Path("a"), "aaaa2", False)

b1 = MockNode(Path("b"), "bbbb1", False)
b2 = MockNode(Path("b"), "bbbb2", False)

c1 = MockNode(Path("c"), "cccc1", False)
c2 = MockNode(Path("c"), "cccc2", False)

d1 = MockNode(Path("d"), "dddd1", False)
d2 = MockNode(Path("d"), "dddd2", False)

e1 = MockNode(Path("e"), "eeee1", False)
e2 = MockNode(Path("e"), "eeee2", False)

f1 = MockNode(Path("f"), "ffff1", True)
f2 = MockNode(Path("f"), "ffff2", True)


class BaseTreeDiffTests(TestCase):

    """
    """

    def setUp(self):
        head_nodes = [
            a1, b1, c1
        ]
        index_nodes = [
            a1, b2, d1
        ]
        stage_nodes = [
            a1, b2, d1, e1, f1
        ]

        self.diff = BaseTreeDiff(
            head_nodes,
            index_nodes,
            stage_nodes
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


class BaseTreeDiffTestsNoStage(TestCase):

    """
    """

    def setUp(self):
        head_nodes = [
            a1, b1, c1
        ]
        index_nodes = [
            a1, b2, d1
        ]

        self.diff = BaseTreeDiff(
            head_nodes,
            index_nodes
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
        assert set() == self.diff.untracked

    def test_ignored(self):
        assert set() == self.diff.ignored
