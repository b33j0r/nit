#! /usr/bin/env python
"""
"""
import configparser
from pathlib import Path
from pprint import pprint
from _collections_abc import Mapping
from abc import abstractproperty


class Config(Mapping):

    """
    """

    def __init__(self, parent=None):
        """
        :param parent:
        :return:
        """
        self._parent = parent or {}

    def get(self, key, default=None, recursive=True):
        """
        :param key:
        :param default:
        :param recursive:
        :return:
        """
        if key in self._key_set:
            return self.get(key, default, recursive)
        return self._parent.get(key, default, recursive)

    def set(self, key, value):
        raise TypeError(
            "{} does not support assignment".format(
                self.__class__.__name__
            )
        )

    def save(self, stream=None):
        raise TypeError(
            "{} does not support save".format(
                self.__class__.__name__
            )
        )

    @abstractproperty
    def _key_set(self):
        """
        Keys in this Config, EXCLUDING parent keys.
        :return (set):
        """

    @property
    def key_set(self):
        """
        Keys in this Config, including parent keys.
        :return (set):
        """
        ks = self._key_set
        try:
            ks = ks.union(self._parent.key_set)
        except AttributeError:
            pass
        return ks

    def keys(self):
        return iter(sorted(self.key_set))

    def __getitem__(self, item):
        value = self.get(item, default=RuntimeError)
        if value == RuntimeError:
            raise KeyError(item)
        return value

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __contains__(self, item):
        if item in self._key_set:
            return True
        return self._parent.__contains__(item)

    def __len__(self):
        return sum(1 for k in self)

    def __iter__(self):
        return self.keys()

    def __bool__(self):
        return len(self) > 0

    def __str__(self):
        return "\n".join([
            "{key:<29s} {value:<30s}".format(key=key, value=value)
            for key, value in self.items()
        ])


class DictConfig(Config):

    """
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._data = {}

    @property
    def _key_set(self):
        return set(self._data.keys())

    def get(self, key, default=None, recursive=True):
        try:
            return self._data[key]
        except KeyError:
            pass
        if recursive:
            return super().get(
                key,
                default=default,
                recursive=recursive
            )
        return default


class IniConfig(Config):

    """
    """

    def __init__(self, file_path, parent=None):
        super().__init__(parent=parent)
        self.parser = configparser.ConfigParser()
        self.file_path = Path(file_path)
        self.parser.read(str(self.file_path))

    @property
    def _key_set(self):
        ks = set()
        for section in self.parser.sections():
            for key in self.parser[section]:
                path = "{}.{}".format(section, key)
                ks.add(path)
        return ks

    def get(self, key, default=None, recursive=True):
        section, name = key.split(".")
        try:
            value = self.parser[section][name]
            return value
        except KeyError:
            pass
        if recursive:
            return super().get(
                key,
                default=default,
                recursive=recursive
            )
        return None

    def set(self, key, value):
        section, name = key.split(".")
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser[section][name] = value

    def save(self, stream=None):
        if stream:
            raise NotImplementedError()
        with self.file_path.open('w') as f:
            self.parser.write(f)


class BaseConfigBuilder(DictConfig):

    """
    """
    def __init__(self, paths):
        self.default_config = DictConfig()
        self.global_config = IniConfig(
            paths.global_config,
            parent=self.default_config
        )
        self.repo_config = IniConfig(
            paths.config,
            parent=self.global_config
        )
        super().__init__(
            parent=self.repo_config
        )


if __name__ == "__main__":
    ini_config = IniConfig("test.ini")
    assert ini_config["user.name"] == "Test"

    pprint(list(ini_config.keys()))

    config = DictConfig(parent=ini_config)
    config["user.name"] = "Brian"
    assert config["user.name"] == "Brian"
    pprint(list(config.keys()))
    assert len(config) == 2

    config2 = DictConfig(parent=config)
    assert config2["user.name"] == "Brian"
    pprint(list(config2.keys()))
    assert len(config2) == 2

    config2["user.name"] = "Mister"
    assert config["user.name"] == "Brian"
    assert config2["user.name"] == "Mister"
    assert len(config2) == 2

    assert ini_config["user.name"] == "Test"
