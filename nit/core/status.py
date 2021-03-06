#! /usr/bin/env python
"""
"""
from abc import ABCMeta, abstractproperty, abstractmethod

from nit.core.diff import BaseTreeDiff
from nit.core.errors import NitRefNotFoundError, \
    NitObjectNotFoundError
from nit.core.objects.tree import Tree
from nit.core.log import getLogger


logger = getLogger(__name__)


class StatusStrategy(metaclass=ABCMeta):
    """
    """

    @abstractproperty
    def clean(self):
        """
        :return:
        """

    @abstractproperty
    def branch(self):
        """
        """

    @abstractproperty
    def added(self):
        pass

    @abstractproperty
    def removed(self):
        pass

    @abstractproperty
    def unmodified(self):
        pass

    @abstractproperty
    def modified(self):
        pass

    @abstractproperty
    def untracked(self):
        pass

    @abstractproperty
    def ignored(self):
        pass


class BaseStatusStrategy(StatusStrategy):

    """
    """

    def __init__(
        self, head, index, working,
        ignorer=None, current_branch=None,
        tree_diff_cls=BaseTreeDiff,
        head_commit=None
    ):
        self._ignorer = ignorer or (lambda n: False)
        self.current_branch = current_branch
        self.head_index = tree_diff_cls(head, index)
        self.head_working = tree_diff_cls(head, working)
        self.index_working = tree_diff_cls(index, working)
        self.head_commit = head_commit

    @classmethod
    def from_repo(
        cls, repo, ignorer=None, tree_diff_cls=BaseTreeDiff
    ):
        try:
            head_commit = repo.storage.resolve_symbolic_ref(
                "HEAD"
            )
        except NitObjectNotFoundError:
            head_commit = None

        try:
            head_tree_key = head_commit.tree_key
            head = repo.storage.get_object(
                head_tree_key
            )
        except AttributeError:
            head = Tree()

        index = repo.storage.get_index()
        working = repo.storage.get_working_tree()

        current_branch = repo.get_current_branch()

        return cls(
            head, index, working,
            ignorer=ignorer,
            current_branch=current_branch,
            tree_diff_cls=tree_diff_cls,
            head_commit=head_commit
        )

    @property
    def clean(self):
        """
        :return:
        """
        return not (
            self.added or
            self.modified or
            self.removed or
            self.untracked
        )

    @property
    def branch(self):
        """
        """
        raise NotImplementedError()

    @property
    def added(self):
        """
        Nodes whose paths are found in the index tree but
        not the head tree.
        """
        return self.head_index.added

    @property
    def removed(self):
        """
        Nodes whose paths are found in the head tree but
        not the index tree.
        """
        return (
            self.head_index.removed.union(
                self.head_working.removed
            )
        )

    @property
    def unmodified(self):
        """
        Nodes whose paths are found in the head tree and
        the index tree, but which have different keys.
        """
        return self.head_index.unmodified

    @property
    def unstaged(self):
        """
        Nodes whose paths are found in the working tree but
        whose keys are not in the index, and are not ignored.
        """
        return set(
            n for n
            in self.index_working.modified.union(
                self.index_working.added
            )
            if not self._ignorer(n.path)
        ) - self.untracked

    @property
    def modified(self):
        """
        Nodes whose paths are found in the head tree and
        the index tree, but which have different keys.
        """
        return self.head_index.modified

    @property
    def untracked_all(self):
        """
        Nodes whose paths are found in the working tree
        but not in the index tree.
        """
        return self.index_working.added

    @property
    def untracked(self):
        """
        Nodes whose paths are found in the working tree
        but not in the index tree, and are not ignored.
        """
        return set(
            n for n
            in self.untracked_all
            if not self._ignorer(n.path)
        )

    @property
    def ignored(self):
        """
        Nodes whose paths are found in the working tree
        but not in the index tree, but are ignored.
        """
        return set(
            n for n
            in self.untracked_all
            if self._ignorer(n.path)
        )


class StatusFormatter(metaclass=ABCMeta):

    """
    """

    @abstractmethod
    def format(self, status):
        """
        :return (str):
        """
