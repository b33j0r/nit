#! /usr/bin/env python
"""
"""
from abc import ABCMeta, abstractproperty

from nit.core.log import getLogger


logger = getLogger(__name__)


class TreeDiffFormatter:

    """
    """

    def format_node(
            self, node,
            key_color=logger.Fore.LIGHTBLACK_EX,
            path_color=logger.Fore.RESET
    ):
        return (
            key_color + "{n.key}" +
            logger.Fore.RESET + " " +
            path_color + "{n.path}" +
            logger.Fore.RESET
        ).format(n=node)

    def format_nodes(
            self,
            nodes,
            name,
            header_color=logger.Fore.LIGHTWHITE_EX,
            key_color=logger.Fore.LIGHTBLACK_EX,
            path_color=logger.Fore.RESET
    ):
        if not nodes:
            return ""

        parts = [
            header_color,
            name,
            logger.Fore.RESET,
            "\n"
        ]

        node_parts = [
            self.format_node(
                node,
                key_color,
                path_color
            )
            for node in nodes
        ]
        node_parts_str = "\n".join(node_parts)
        parts.append(node_parts_str)
        parts.append("\n\n")
        return "".join(parts)

    def format(self, diff):
        parts = [
            self.format_nodes(
                diff.added,
                "Added",
                logger.Fore.GREEN
            ),
            self.format_nodes(
                diff.removed,
                "Removed",
                logger.Fore.RED
            ),
            self.format_nodes(
                diff.modified,
                "Modified",
                logger.Fore.YELLOW
            ),
            self.format_nodes(
                diff.unstaged,
                "Unstaged",
                logger.Fore.LIGHTCYAN_EX
            ),
            self.format_nodes(
                diff.untracked,
                "Untracked",
                logger.Fore.LIGHTCYAN_EX
            )
        ]
        if False:
            parts += [
                self.format_nodes(
                    diff.ignored,
                    "Ignored",
                    logger.Fore.LIGHTBLACK_EX
                )
            ]
        s = "".join(parts)
        if s.endswith("\n\n"):
            s = s[:-1]

        if not s.strip():
            return "No changes detected"

        return s


class TreeDiff(metaclass=ABCMeta):

    """
    """

    @abstractproperty
    def added(self):
        """
        Nodes with file paths in to_tree, but not from_tree

        :return (set):
        """
        pass

    @abstractproperty
    def removed(self):
        """
        Nodes with file paths in from_tree, but not to_tree

        :return (set):
        """
        pass

    @abstractproperty
    def modified(self):
        """
        Nodes sharing file paths in from_tree and to_tree
        but with differing key values

        :return (set):
        """
        pass

    @abstractproperty
    def unmodified(self):
        """
        Nodes perfectly matching in both trees

        :return (set):
        """
        pass


class BaseTreeDiff(TreeDiff):

    def __init__(
            self,
            from_tree,
            to_tree
    ):
        self.from_nodes = set(from_tree or [])
        self.to_nodes = set(to_tree or [])

        # Associate paths with nodes
        self.from_paths = {
            n.path: n for n in self.from_nodes
        }
        self.from_paths_set = set(self.from_paths)

        self.to_paths = {
            n.path: n for n in self.to_nodes
        }
        self.to_paths_set = set(self.to_paths)

        # Associate keys with nodes
        self.from_keys = {
            n.key: n for n in self.from_nodes
        }
        self.from_keys_set = set(self.from_keys)

        self.to_keys = {
            n.key: n for n in self.to_nodes
        }
        self.to_keys_set = set(self.to_keys)

        # Find the nodes with paths in both trees
        self.both_paths_set = self.to_paths_set.intersection(
            self.from_paths_set
        )

    @property
    def added(self):
        """
        Nodes with file paths in to_tree, but not from_tree

        :return (set):
        """
        return {
            self.to_paths[k]
            for k in self.to_paths_set - self.from_paths_set
        }

    @property
    def removed(self):
        """
        Nodes with file paths in from_tree, but not to_tree

        :return (set):
        """
        return {
            self.from_paths[k]
            for k in self.from_paths_set - self.to_paths_set
        }

    @property
    def modified(self):
        """
        Nodes sharing file paths in from_tree and to_tree
        but with differing key values

        :return (set):
        """
        return {
            self.to_paths[k] for k in self.both_paths_set
            if self.to_paths[k].key != self.from_paths[k].key
        }

    @property
    def unmodified(self):
        """
        Nodes perfectly matching in both trees

        :return (set):
        """
        return self.from_nodes.intersection(
            self.to_nodes
        )
