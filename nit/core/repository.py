#! /usr/bin/env python
"""
"""
from abc import abstractmethod
from abc import ABCMeta


class Repository(metaclass=ABCMeta):
    @abstractmethod
    def create(self, force):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def add(self, relative_file_path):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def checkout(self):
        pass
