#! /usr/bin/env python
"""
"""
from tempfile import TemporaryDirectory
from unittest import TestCase
from pathlib import Path
from nit.core.ignore import RelativeIgnorePredicate, RegexIgnorePredicate


class RelativeIgnorePredicateTests(TestCase):

    """
    """

    class DummyPredicate(RelativeIgnorePredicate):
        def _ignore_relative(self, relative_file_path):
            return "ignore" in str(relative_file_path)

    def setUp(self):
        self.predicate = self.DummyPredicate()

    def test_not_relative(self):
        assert self.predicate.ignore(
            "/fake", "/notfake"
        )

    def test_relative_ignore(self):
        assert self.predicate.ignore(
            "/fake", "/fake/ignore"
        )

    def test_relative_included(self):
        assert not self.predicate.ignore(
            "/fake", "/fake/include"
        )


class RegexIgnorePredicateTests(TestCase):

    """
    """

    def setUp(self):
        self.predicate = RegexIgnorePredicate(
            r"ignore([^d]|$)"
        )

    def test_not_relative(self):
        assert self.predicate.ignore(
            "/fake", "/notfake"
        )

    def test_relative_ignore(self):
        assert self.predicate.ignore(
            "/fake", "/fake/ignore"
        )

    def test_relative_included(self):
        assert not self.predicate.ignore(
            "/fake", "/fake/include"
        )

    def test_relative_included_regex(self):
        assert not self.predicate.ignore(
            "/fake", "/fake/ignored"
        )

    def test_relative_ignored_regex(self):
        assert self.predicate.ignore(
            "/fake", "/fake/ignores"
        )


# class IgnoreStrategyPurePathTests(TestCase):
#
#     """
#     """
#
#     def setUp(self):
#         project_dir = Path("/fake")
#         self.paths = BasePaths(project_dir, verify=False)
#         self.ignorer = BaseIgnoreStrategy(
#             project_dir, [
#                 "ignore_me",
#                 "\\.pyc$"
#             ]
#         )
#
#     def test_ignore_repo(self):
#         assert self.ignorer.ignore(self.paths.repo)
#
#     def test_ignore_file_in_repo(self):
#         ignored_file = self.paths.repo/"include_me"
#         assert self.ignorer.ignore(ignored_file)
#
#     def test_ignore_file_in_project(self):
#         ignored_file = self.paths.project/"ignore_me"
#         assert self.ignorer.ignore(ignored_file)
#
#     def test_ignore_file_outside_of_project(self):
#         ignored_file = self.paths.project.parent/"include_me"
#         assert self.ignorer.ignore(ignored_file)
#
#     def test_not_ignore_file_in_project(self):
#         not_ignored_file = self.paths.project/"main.py"
#         assert not self.ignorer.ignore(not_ignored_file)
#
#     def test_ignore_file_pattern_in_project(self):
#         ignored_file = self.paths.project/"main.pyc"
#         assert self.ignorer.ignore(ignored_file)
#
#
# class IgnoreStrategyFilesystemTests(IgnoreStrategyPurePathTests):
#
#     """
#     """
#
#     def setUp(self):
#         self.temp_dir = TemporaryDirectory()
#         self.project_dir = Path(self.temp_dir.name)
#         self.paths = BasePaths(self.project_dir, verify=False)
#         self.paths.repo.mkdir()
#         self.ignorer = BaseIgnoreStrategy(
#             self.paths.project, [
#                 "ignore_me",
#                 ".py[cod]"
#             ]
#         )
#         self.ignored_files = {
#             self.paths.repo/"ignore_me",
#             self.paths.repo/"dont_include_me",
#             self.paths.project/"ignore_me"
#         }
#         self.included_files = {
#             self.paths.project/"include_me"
#         }
#         self.all_files = self.ignored_files.union(self.included_files)
#         for f in self.all_files:
#             f.touch()
#
#     def tearDown(self):
#         self.temp_dir.cleanup()
#
#     def test_exists(self):
#         assert self.paths.repo.exists()
#         for f in self.all_files:
#             assert f.exists()
#
#     def test_ignored_file(self):
#         assert self.ignorer.ignore(
#             self.paths.project/"ignore_me"
#         )
#
#     def test_ignored_files(self):
#         for f in self.ignored_files:
#             assert self.ignorer.ignore(f)
#
#     def test_included_files(self):
#         for f in self.included_files:
#             assert not self.ignorer.ignore(f)
