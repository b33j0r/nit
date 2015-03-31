#! /usr/bin/env python
"""
"""


class StagingStrategy:
    """
    """
    def __init__(self, storage):
        self.storage = storage

    def add(self, file_path):
        raise NotImplementedError()

    @property
    def files(self):
        raise NotImplementedError()
