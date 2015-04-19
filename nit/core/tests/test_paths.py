#! /usr/bin/env python
"""
"""
from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from nit.core.errors import NitExpectedError

from nit.core.paths import BasePaths


class BasePathsTests(TestCase):

    """
    """

    def __init__(self, methodName='runTest'):
        super().__init__(methodName=methodName)
        self.repo_name = ".nit"

    def setUp(self):
        self.project_dir_td = TemporaryDirectory()
        self.project_dir = Path(self.project_dir_td.name)
        self.repo_dir = self.project_dir/self.repo_name
        self.repo_dir.mkdir()
        assert self.project_dir.exists()
        self.paths = BasePaths(self.project_dir)
        self.paths.objects.mkdir()
        self.paths.refs.mkdir()

    def tearDown(self):
        self.project_dir_td.cleanup()

    def test_find_repo_dir_in_project_dir(self):
        repo_path = self.paths.find_repo_dir(
            self.project_dir, ".nit"
        )
        self.assertEqual(
            repo_path,
            self.repo_dir
        )

    def test_find_repo_dir_in_project_subdir(self):
        subdir = self.project_dir/"subdir"
        subdir.mkdir()
        repo_path = self.paths.find_repo_dir(
            subdir, ".nit"
        )
        self.assertEqual(
            repo_path,
            self.repo_dir
        )

    def test_repo_str(self):
        self.assertEqual(
            self.paths.repo_str, str(self.repo_dir)
        )

    def test_repo_name(self):
        self.assertEqual(
            self.paths.repo_name, self.repo_name
        )

    def test_repo(self):
        self.assertEqual(
            self.paths.repo, self.repo_dir
        )

    def test_objects_name(self):
        self.assertEqual(
            self.paths.objects_name, "objects"
        )

    def test_objects(self):
        self.assertEqual(
            self.paths.objects,
            self.repo_dir/self.paths.objects_name
        )

    def test_refs_name(self):
        self.assertEqual(
            self.paths.refs_name, "refs"
        )

    def test_refs(self):
        self.assertEqual(
            self.paths.refs,
            self.repo_dir/self.paths.refs_name
        )

    def test_index_name(self):
        self.assertEqual(
            self.paths.index_name, "index"
        )

    def test_index(self):
        self.assertEqual(
            self.paths.index,
            self.repo_dir/self.paths.index_name
        )

    def test_head_name(self):
        self.assertEqual(
            self.paths.head_name, "HEAD"
        )

    def test_head(self):
        self.assertEqual(
            self.paths.head,
            self.repo_dir/self.paths.head_name
        )

    def test_get_object_path(self):
        obj_path = self.paths.get_object_path(
            "a", must_exist=False
        )
        self.assertEqual(
            obj_path,
            self.paths.objects/"a"
        )

    def test_get_object_path_doesnt_exist(self):
        self.assertRaises(
            NitExpectedError,
            self.paths.get_object_path,
            "a",
            must_exist=True
        )

    def test_get_object_path_exists_wildcard(self):
        c1 = self.paths.objects/"c1a"
        c2 = self.paths.objects/"c2a"
        c1.touch()
        c2.touch()

        obj_path = self.paths.get_object_path("c1")
        self.assertEqual(
            obj_path,
            self.paths.objects/"c1a"
        )

    def test_get_object_path_errors_on_multiple_matches(self):
        c1 = self.paths.objects/"c1"
        c2 = self.paths.objects/"c2"
        c1.touch()
        c2.touch()

        self.assertRaises(
            NitExpectedError,
            self.paths.get_object_path,
            "c",
            must_exist=True
        )

    def test_get_canonical_object_path(self):
        canonical_object_path = (
            self.paths.get_canonical_object_path("foo")
        )
        self.assertEqual(
            canonical_object_path,
            self.paths.objects/"foo"
        )

    def test_find_object_paths_matching_nothing(self):
        search_results = (
            self.paths.find_object_paths_matching("foo")
        )

        self.assertEqual(
            search_results,
            []
        )

    def test_find_object_paths_matching_one(self):
        c1 = self.paths.objects/"c1"
        c1.touch()

        search_results = (
            self.paths.find_object_paths_matching("c")
        )

        self.assertEqual(
            search_results,
            [
                self.paths.objects/"c1"
            ]
        )

    def test_find_object_paths_matching_two(self):
        c1 = self.paths.objects/"c1"
        c2 = self.paths.objects/"c2"
        c1.touch()
        c2.touch()

        search_results = (
            self.paths.find_object_paths_matching("c")
        )

        self.assertEqual(
            search_results,
            [
                self.paths.objects/"c1",
                self.paths.objects/"c2"
            ]
        )
