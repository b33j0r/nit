#! /usr/bin/env python
"""
"""
from abc import ABCMeta
from contextlib import contextmanager
from nit.core.storage import Storage


class Operation(metaclass=ABCMeta):

    """
    """


class Transaction(metaclass=ABCMeta):

    """
    Groups a series of operations.
    """

    @classmethod
    @contextmanager
    def begin(cls, parent):
        """
        Use this method to wrap a transaction scope in client
        code. If the scope completes successfully, the transaction
        is finalized. If an exception occurs, the transaction is
        aborted, and the exception is re-raised.

        :param parent:
        :return:
        """
        transaction = Transaction(parent)
        try:
            yield transaction
            transaction.finalize()
        except Exception:
            transaction.abort()
            raise

    def finalize(self):
        print("finalize")

    def abort(self):
        print("abort")


class StorageTransaction(Transaction, Storage):

    """
    A storage proxy. Allows multiple database operations to
    be performed on a tentative basis in case a failure occurs
    and the overall operation needs to be aborted.
    """

    def __init__(self, parent):
        self.parent = parent

    def destroy(self, ignore_errors=True):
        pass

    def create(self, force=False):
        pass

    def put_ref(self, ref, key):
        pass

    def put(self, storable):
        pass

    def get_treeish(self, treeish):
        pass

    def get_ref(self, ref):
        pass

    def get_object(self, keyish):
        pass

    def get_index(self):
        pass

    def exists(self):
        pass


with Transaction.begin(None) as transaction:
    transaction.exists()

with Transaction.begin(None) as transaction:
    raise NotImplementedError()
