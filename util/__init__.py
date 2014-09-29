
from attr import temporary_attr
from cache import cached_property
from rawdb.util.io import BinaryIO


def lget(lst, idx, default=None):
    """Gets an item from a list if the list supports it. Otherwise it returns
    the default value.

    Parameters
    ----------
    lst : list
        Target list
    idx : int
        Index of list to get
    default : mixed
        Value to return if idx isn't in lst

    Returns
    -------
    value : mixed
        lst[idx] if available, else default.
    """
    try:
        return lst[idx]
    except IndexError:
        return default


__all__ = ['cached_property', 'temporary_attr', 'BinaryIO', 'lget']
