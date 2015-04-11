#! /usr/bin/env python
"""
"""
import sys
import argparse
from abc import ABCMeta
from functools import wraps

from nit.core.log import getLogger
from nit.core.errors import NitUserError, NitInternalError


logger = getLogger(__name__)


def map_args(arg_mappings=None, kwarg_mappings=None):
    arg_mappings = arg_mappings or []
    kwarg_mappings = kwarg_mappings or []

    def map_args_decorator(fn):

        @wraps(fn)
        def map_args_implementation(*unmapped_args, parsed_args=None, **kwargs):
            args = []
            for arg_name in arg_mappings:
                args.append(getattr(parsed_args, arg_name))

            for kwarg_mapping in kwarg_mappings:
                try:
                    parsed_kwarg_name, kwarg_name = kwarg_mapping
                except ValueError:
                    parsed_kwarg_name, kwarg_name = kwarg_mapping, kwarg_mapping
                kwargs[kwarg_name] = getattr(parsed_args, parsed_kwarg_name)

            args = list(unmapped_args) + args

            return fn(*args, **kwargs)

        return map_args_implementation

    return map_args_decorator


class RepositoryProxy:
    """

    """

    def __init__(self, repo):
        self.repo = repo

    @map_args(kwarg_mappings=["force"])
    def init(self, force=None):
        self.repo.create(force=force)

    def status(self, args):
        print("STATUS was called with {}".format(args))

    @map_args(arg_mappings=["files"])
    def add(self, files):
        self.repo.add(*files)

    @map_args(arg_mappings=["key"])
    def cat(self, key):
        s = self.repo.cat(key)
        # the logger already adds a newline
        if s.endswith("\n"):
            s = s[:-1]
        logger.info(s)

    def commit(self, args):
        print("COMMIT was called with {}".format(args))

    def checkout(self, args):
        print("CHECKOUT was called with {}".format(args))


class ParserFactory(metaclass=ABCMeta):

    """
    """

    def build_parser(self, repository, **kwargs):
        pass


class BaseParserFactory(ParserFactory):

    """
    """

    DEFAULT_DESCRIPTION = """
        The commandline client for nit, a pythonic
        framework for experimenting with git-like
        version control systems.

        http://www.github.com/b33j0r/nit
    """

    DEFAULT_INIT_HELP = """
        Initializes an empty repository
    """

    def build_parser(self, repository, **kwargs):
        """

        :param repository:
        :return:
        """

        # Root parser for 'nit' command
        parser = argparse.ArgumentParser(
            description=self.DEFAULT_DESCRIPTION
        )
        subparsers = parser.add_subparsers()

        # Sub-parser for 'test' command
        parser_add = subparsers.add_parser("test")
        parser_add.set_defaults(
            func=parser_test
        )

        # Sub-parser for 'init' command
        parser_init = subparsers.add_parser(
            "init",
            help=self.DEFAULT_INIT_HELP
        )
        parser_init.set_defaults(
            func=repository.init
        )
        parser_init.add_argument(
            '--force',
            action='store_true'
        )

        # Sub-parser for 'status' command
        parser_status = subparsers.add_parser("status")
        parser_status.set_defaults(
            func=repository.status
        )

        # Sub-parser for 'add' command
        parser_add = subparsers.add_parser("add")
        parser_add.set_defaults(
            func=repository.add
        )
        parser_add.add_argument("files", nargs="+")

        # Sub-parser for 'cat' command
        parser_cat = subparsers.add_parser("cat")
        parser_cat.set_defaults(
            func=repository.cat
        )
        parser_cat.add_argument("key")

        # Sub-parser for 'commit' command
        parser_commit = subparsers.add_parser("commit")
        parser_commit.set_defaults(
            func=repository.commit
        )

        # Sub-parser for 'checkout' command
        parser_checkout = subparsers.add_parser("checkout")
        parser_checkout.set_defaults(
            func=repository.checkout
        )

        return parser


class NitLoggerTestException(Exception):
    def __init__(self):
        super().__init__("Testing, testing, 1, 2, 3!")


def parser_test(*args, **kwargs):
    raise NitLoggerTestException()


def main(*args):
    import os
    import colorama
    colorama.init()

    from nit.components.nit.repository import NitRepository

    args = args or sys.argv
    nit_repo = NitRepository(os.getcwd())
    repo = RepositoryProxy(nit_repo)
    parser_factory = BaseParserFactory()
    parser = parser_factory.build_parser(repo)
    args = parser.parse_args(args)

    try:
        args.func(parsed_args=args)
        return 0

    except NitUserError as exc:
        logger.error(str(exc))

    except NitInternalError as exc:
        logger.critical(str(exc))

    except NitLoggerTestException as exc:
        logger.critical(str(exc))
        logger.error(str(exc))
        logger.warn(str(exc))
        logger.debug(str(exc))
        logger.info(str(exc))

    except Exception as exc:
        import traceback
        logger.critical("[Unhandled Error] " + str(exc))
        logger.debug("\n" + traceback.format_exc())

    finally:
        colorama.deinit()

    return 1