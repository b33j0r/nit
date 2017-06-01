from nit.components.git.repository import GitRepository
from nit.components.nit.repository import NitRepository
from nit.core.errors import NitExpectedError


__all__ = [
    'get_repository_cls',
]


repositories = {
    'nit': NitRepository,
    'git': GitRepository,
}


def get_repository_cls(driver):
    cls = repositories.get(driver)
    if not cls:
        raise NitExpectedError('"{}" is not a valid driver'.format(driver))
    return cls
