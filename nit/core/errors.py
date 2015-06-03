#! /usr/bin/env python
"""
"""


class NitError(Exception):
    """
    """


class NitUnexpectedError(Exception):
    """
    """


class NitInternalError(NitUnexpectedError):
    """
    """


class NitExpectedError(Exception):
    """
    """


class NitUserError(NitExpectedError):
    """
    """


class NitObjectNotFoundError(NitExpectedError):
    """
    """


class NitRefNotFoundError(NitExpectedError):
    """
    """
