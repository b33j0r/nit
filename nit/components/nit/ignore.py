#! /usr/bin/env python
"""
"""
from nit.core.ignore import (
    PathspecIgnorePredicate,
    CompoundIgnorePredicate
)


class NitIgnoreStrategy:

    """
    """

    def __init__(self, paths):
        self.base_path = paths.project
        try:
            with paths.ignore.open('r', encoding='utf-8') as f:
                lines = f.readlines()
            predicates = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                predicate = PathspecIgnorePredicate(line)
                predicates.append(predicate)
        except FileNotFoundError:
            predicates = []

        # Always ignore the repo dir
        predicates = [
            PathspecIgnorePredicate(
                paths.repo_name + "/"
            )
        ] + predicates

        self.predicate = CompoundIgnorePredicate(
            predicates
        )

    def ignore(self, file_path):
        return self.predicate.ignore(
            self.base_path, file_path
        )
