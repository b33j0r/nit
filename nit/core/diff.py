#! /usr/bin/env python
"""
"""

from nit.core.log import getLogger


logger = getLogger(__name__)


class TreeDiff:

    """
    """

    def __init__(self, tree_from, tree_to):
        logger.debug("Creating TreeDiff")
        self.tree_from = tree_from
        self.tree_to = tree_to
        self.added_nodes, self.modified_nodes, self.removed_nodes = self._diff()

    def _diff(self):
        a_key_to_node = self.tree_from.key_to_node
        b_key_to_node = self.tree_to.key_to_node

        a_file_to_node = self.tree_from.file_to_node
        b_file_to_node = self.tree_to.file_to_node

        changes = self.tree_to.node_set ^ self.tree_from.node_set

        added_files = self.tree_to.file_set - self.tree_from.file_set
        removed_files = self.tree_from.file_set - self.tree_to.file_set

        modified_files = set([
            a_key_to_node.get(n.key, b_key_to_node.get(n.key)).path
            for n in changes
            if (
                n.path not in added_files and
                n.path not in removed_files
            )
        ])

        modified_nodes = sorted(set([
            self.tree_to.file_to_node[path] for path in modified_files
        ]))

        added_nodes = sorted([
            b_file_to_node[f] for f in added_files
        ])

        removed_nodes = sorted([
            a_file_to_node[f] for f in removed_files
        ])

        return added_nodes, modified_nodes, removed_nodes

    def __str__(self):
        # This needs some cleaning up... haven't decided how to do it yet

        logger.debug("Rendering string for TreeDiff")

        def node_template(color):
            color = logger.Fore.LIGHTBLACK_EX
            return (
                color + "{n.key}" + logger.Fore.RESET + " " + "{n.path}"
            )

        s = "{}{}{}".format(
            (
                logger.Fore.LIGHTWHITE_EX +
                logger.Fore.GREEN +
                "Added" + logger.Fore.RESET +
                "\n" + logger.Fore.RESET +
                "\n".join(
                    node_template(logger.Fore.GREEN).format(n=n) for n in self.added_nodes
                ) + "\n\n"
            ) if self.added_nodes else "",

            (
                logger.Fore.LIGHTWHITE_EX +
                logger.Fore.YELLOW +
                "Modified" + logger.Fore.RESET +
                "\n" + logger.Fore.RESET +
                "\n".join(
                    node_template(logger.Fore.YELLOW).format(n=n) for n in self.modified_nodes
                ) + "\n\n"
            ) if self.modified_nodes else "",

            (
                logger.Fore.LIGHTWHITE_EX +
                logger.Fore.RED +
                "Removed" + logger.Fore.RESET +
                "\n" + logger.Fore.RESET +
                "\n".join(
                    node_template(logger.Fore.RED).format(n=n) for n in self.removed_nodes
                ) + "\n\n"
            ) if self.removed_nodes else ""
        )
        if s.endswith("\n\n"):
            s = s[:-1]
        return s
