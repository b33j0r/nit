#! /usr/bin/env python
"""
"""
from _collections_abc import Iterable, Sized, Container, Mapping
from abc import abstractmethod, ABCMeta

class Config:

    """
    """

    def __getitem__(self, item):
        return 1

    def __iter__(self):
        return [1, 1]

    def __contains__(self, item):
        return item == 1

    def __len__(self):
        return 2

config = Config()
assert isinstance(config, Iterable)
assert isinstance(config, Sized)
assert isinstance(config, Container)
assert isinstance(config, Mapping)
