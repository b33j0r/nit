#! /usr/bin/env python
"""
"""
from abc import abstractmethod, abstractproperty
from abc import ABCMeta


class Repository(metaclass=ABCMeta):
    @abstractproperty
    def exists(self):
        pass

    @abstractmethod
    def create(self, force):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def add(self, relative_file_path):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def checkout(self, treeish):
        """
        :param treeish:
        :return:
        """
