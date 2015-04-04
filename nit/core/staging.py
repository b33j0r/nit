#! /usr/bin/env python
"""
"""
from abc import ABCMeta, abstractmethod


class Stage(metaclass=ABCMeta):

    """
    An observable interface that notifies observers when the
    staging area is modified.
    """

    @abstractmethod
    def subscribe(self, observer):
        pass


class StageObserver(metaclass=ABCMeta):

    """
    An observer interface that listens to notifications about
    modifications to the staging area.
    """

    def on_file_added(self):
        pass

    def on_file_removed(self):
        pass

    def on_file_changed(self):
        pass


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
