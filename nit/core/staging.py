#! /usr/bin/env python
"""
"""
from abc import ABCMeta, abstractmethod


class Stage:
    """
    """
    def __init__(self, project_dir, ignore_strategy_cls=PathspecIgnoreStrategy):
        self.storage = storage

    def add(self, file_path):
        raise NotImplementedError()

    @property
    def files(self):
        raise NotImplementedError()
