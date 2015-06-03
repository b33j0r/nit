#! /usr/bin/env python
"""
"""
from nit.core.log import getLogger
from nit.components.base.status import BaseStatusFormatter


logger = getLogger(__name__)


class GitStatusFormatter(BaseStatusFormatter):

    """
    """
    @property
    def header_message(self):
        return None

    @property
    def branch_message(self):
        branch_message = "On branch {branch}\n"
        return branch_message.format(branch=self.status.current_branch)

    @property
    def diff_message(self):
        diff_message = "Your branch is up-to-date with {branch:!r}."
        return diff_message.format(branch=self.status.current_branch)

    @property
    def staged_message(self):
        msg = """
Changes to be committed:
  (use "nit reset HEAD <file>..." to unstage)

{}
""".lstrip()

        statuses = {
            "added": "new file",
            "modified": "modified",
            "removed": "deleted"
        }

        index_statuses = sorted(
            [
                (f, statuses["added"])
                for f in self.status.added
            ] + [
                (f, statuses["modified"])
                for f in self.status.modified
            ] + [
                (f, statuses["removed"])
                for f in self.status.removed
            ],
            key=lambda a: a[0].path
        )

        index_lines = list(
            logger.Fore.GREEN + "\t" +
            "{label:<12s}".format(label=status+":") +
            str(f.path) +
            logger.Fore.RESET
            for (f, status) in index_statuses
        )

        if not index_lines:
            return None
        return msg.format("\n".join(index_lines))

    @property
    def unstaged_message(self):
        msg = """
Changes not staged for commit:
  (use "nit add <file>..." to update what will be committed)
  (use "nit checkout -- <file>..." to discard changes in working directory)

{}
""".lstrip()

        statuses = {
            "added": "new file",
            "modified": "modified",
            "removed": "deleted"
        }

        index_statuses = sorted(
            [
                (f, statuses["modified"])
                for f in self.status.unstaged
            ],
            key=lambda a: a[0].path
        )

        index_lines = list(
            logger.Fore.RED + "\t" +
            "{label:<12s}".format(label=status+":") +
            str(f.path) +
            logger.Fore.RESET
            for (f, status) in index_statuses
        )

        if not index_lines:
            return None
        return msg.format("\n".join(index_lines))

    @property
    def untracked_message(self):
        msg = """
Untracked files:
  (use "nit add <file>..." to include in what will be committed)

{}
""".lstrip()

        index_statuses = sorted(
            [
                f for f in self.status.untracked
            ],
            key=lambda a: a.path
        )

        index_lines = list(
            logger.Fore.RED + "\t" +
            str(f.path) +
            logger.Fore.RESET
            for f in index_statuses
        )

        if not index_lines:
            return None
        return msg.format("\n".join(index_lines))

    @property
    def footer_message(self):
        return """
no changes added to commit (use "git add" and/or "git commit -a")
""".strip() if not (
            self.status.added or
            self.status.removed or
            self.status.modified
        ) else ""

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
