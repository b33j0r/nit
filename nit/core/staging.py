#! /usr/bin/env python
"""
"""
from abc import ABCMeta, abstractmethod
from nit.core.diff import TreeDiff


class Stage:

    """
    Manages the index and reconciles it
    with the working tree.
    """

    def __init__(self, paths):
        self.paths = paths

    @property
    def index(self):
        raise NotImplementedError()

    def add(self, relative_file_path):
        raise NotImplementedError()

    def remove(self, relative_file_path):
        raise NotImplementedError()

    @property
    def files(self):
        raise NotImplementedError()


class StageDiff(TreeDiff):

    """
    """

    def __init__(self, tree_from, tree_to, working_tree):
        super().__init__(tree_from, tree_to)
        self.working_tree = working_tree


