#! /usr/bin/env python
"""

"""
import abc
from os.path import expanduser
from pathlib import Path

from nit.core.errors import NitUserError, NitObjectNotFoundError
from nit.core.log import getLogger


logger = getLogger(__name__)


class Paths(metaclass=abc.ABCMeta):

    """
    A strategy class that determines the file system
    paths for a specific repository implementation.

    For git or nit, this means figuring out where the
    "objects", "index", and "HEAD", etc, are.

    A Paths implementation shall return a
    `pathlib.Path` object for any property or method
    not post-fixed by "_name" or "_str"; if you need
    a string and no _str accessor exists, remember to
    convert in your client code.
    """


class BasePaths(Paths):

    """
    A starting point for implementing a git-like
    (nit-like) Paths interface.
    """

    def __init__(
            self,
            current_working_dir_path,
            repo_name=".nit",
            verify=True
    ):
        self.current_working_dir = Path(
            current_working_dir_path
        )

        # Due diligence
        if verify:
            if not self.current_working_dir.exists():
                raise NitUserError(
                    "Current working directory"
                    "does not exist: {}".format(
                        self.current_working_dir
                    )
                )

            if not self.current_working_dir.is_dir():
                raise NitUserError(
                    "Current working directory"
                    "is not a directory (?): {}".format(
                        self.current_working_dir
                    )
                )

        self._repo_name = repo_name
        self._repo = None

    def __getattr__(self, name):
        """
        Since every attribute of Paths returns a
        `pathlib.Path`, we provide a convenient mechanism
        to get a string result for every such attribute
        :param name:
        :return:
        """
        if name.endswith("_str"):
            attr = getattr(self, name[:-4])
            if not isinstance(attr, Path):
                raise AttributeError(
                    "_str postfixes are reserved "
                    "for attributes that normally return "
                    "a Path object, see docstring"
                )
            return str(attr)
        raise AttributeError(name)

    @property
    def global_config_name(self):
        return ".nitconfig"

    @property
    def config_name(self):
        return "config"

    @property
    def repo_name(self):
        """
        e.g. ".git", ".nit"
        """
        return self._repo_name

    @property
    def objects_name(self):
        """
        The name of the subdirectory where a repo
        stores things like blobs, trees, and commits
        """
        return "objects"

    @property
    def refs_name(self):
        """
        The name of the subdirectory where we
        store references to trees
        """
        return "refs"

    @property
    def index_name(self):
        """
        The name of the file that stores our index,
        which is simply a tree that hasn't been
        committed yet
        """
        return "index"

    @property
    def head_name(self):
        """
        The name of a special ref that points to
        the latest commit, usually "HEAD"
        """
        return "HEAD"

    @property
    def ignore_name(self):
        """
        e.g. ".gitignore", ".nitignore"
        """
        return self.repo_name + "ignore"

    @property
    def global_config(self):
        """
        :return (Path):
        """
        return Path(expanduser("~"))/self.global_config_name

    @property
    def config(self):
        """
        :return (Path):
        """
        return self.repo/self.config_name

    @property
    def repo(self):
        """
        :return (Path):
        """
        if not self._repo:
            self._repo = self.find_repo_dir(
                self.current_working_dir, self.repo_name
            )
        return self._repo

    @property
    def project(self):
        """
        :return (Path):
        """
        return self.repo.parent

    @property
    def objects(self):
        """
        :return (Path):
        """
        return self.repo/self.objects_name

    @property
    def refs(self):
        """
        :return (Path):
        """
        return self.repo/self.refs_name

    @property
    def index(self):
        """
        :return (Path):
        """
        return self.repo/self.index_name

    @property
    def head(self):
        """
        :return (Path):
        """
        return self.repo/self.head_name

    @property
    def ignore(self):
        """
        :return (Path):
        """
        return self.project/self.ignore_name

    @classmethod
    def find_repo_dir(cls, cwd, repo_name):
        """
        Given a current working directory, try to find
        the repository dir. Most often, this is the
        current working directory. However, commands can
        also be run from subdirectories of the project
        directory, so we need to search the parent
        directories as well.

        :param cwd:
        :param repo_name:
        :return:
        """
        logger.trace(
            "Working Directory: {}".format(cwd)
        )

        project_dir_candidates = (
            [cwd] + list(cwd.parents)
        )

        for path in project_dir_candidates:
            repo_path = path/repo_name
            if repo_path.exists():
                break

        else:
            logger.trace((
                "No repository exists in '{}' "
                "or its parent directories"
            ).format(cwd))
            return cwd/repo_name

        logger.trace(
            "Repository Directory: {}".format(
                repo_path
            )
        )

        return repo_path

    def get_object_path(self, keyish, must_exist=True):
        """
        :param must_exist:
        :return:
        """
        canonical_path = self.get_canonical_object_path(keyish)

        if canonical_path.exists() and not canonical_path.is_dir():
            return canonical_path

        search_result = self.find_object_paths_matching(keyish)

        # We found our object!
        if len(search_result) == 1:
            return search_result[0]

        # Maybe we are just building a path
        # that doesn't exist yet
        if not must_exist:
            return canonical_path

        # Uh oh, the user specified a key fragment
        # that doesn't resolve to a unique result
        if len(search_result) > 1:
            logger.debug(
                "Multiple objects found:\n{}".format(
                    "\n".join("    " + str(s)
                              for s in search_result)
                )
            )
            raise NitObjectNotFoundError(
                "Multiple objects matching '{}'".format(keyish)
            )

        raise NitObjectNotFoundError(
            "No object matching '{}'".format(keyish)
        )

    def get_canonical_object_path(self, key):
        return self.objects/key

    def iter_object_paths_matching(self, keyish):
        assert keyish
        return (
            p for p in self.objects.glob(keyish + "*")
            if not p.is_dir()
        )

    def find_object_paths_matching(self, keyish):
        return list(
            self.iter_object_paths_matching(keyish)
        )

    def get_ref_relative_path(self, name):
        parts = name.split("/")
        if len(parts) == 1:
            parts = ["heads"] + parts
        if len(parts) == 2:
            parts = ["refs"] + parts
        assert len(parts) <= 3
        return Path(*parts)

    def get_ref_path(self, name):
        relative_path = self.get_ref_relative_path(name)
        return self.repo/relative_path

