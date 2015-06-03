#! /usr/bin/env python
"""
"""
from nit.core.log import getLogger

logger = getLogger(__name__)


class BaseStatusFormatter:

    """
    """

    def __init__(self, status):
        """

        :param status:
        :return:
        """
        self.status = status

    @property
    def header_message(self):
        return "Header"

    @property
    def branch_message(self):
        return "You are in a branch\n"

    @property
    def commit_message(self):
        return (
            "Initial commit\n"
            if self.status.head_commit is None
            else ""
        )

    @property
    def staged_message(self):
        return "Staged"

    @property
    def unstaged_message(self):
        return "Unstaged"

    @property
    def untracked_message(self):
        return "Untracked"

    @property
    def footer_message(self):
        return "Footer"

    @property
    def parts(self):
        return [
            p for p in [
                self.header_message,
                self.branch_message,
                self.commit_message,
                self.staged_message,
                self.unstaged_message,
                self.untracked_message,
                self.footer_message
            ] if p
        ]

    def __str__(self):
        return "\n".join(str(p) for p in self.parts)
