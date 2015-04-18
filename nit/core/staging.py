#! /usr/bin/env python
"""
"""
from abc import ABCMeta, abstractmethod


class Stage:
    """
    """
    def __init__(self, storage):
        self.storage = storage

    def add(self, file_path):
        raise NotImplementedError()

    @property
    def files(self):
        raise NotImplementedError()
