
from attr import temporary_attr, AttrDict
from cache import cached_property
from util.io import BinaryIO


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


def gcf(a, b):
    """Return the Greatest Common Factor of two numbers

    Parameters
    ----------
    a : int
    b : int

    Returns
    -------
    gcf : int
    """
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    """Return the Least Common Multiple of two numbers

    Parameters
    ----------
    a : int
    b : int

    Returns
    -------
    lcm : int
    """
    return a*b / gcf(a, b)


__all__ = ['cached_property', 'temporary_attr', 'AttrDict', 'BinaryIO',
           'lget', 'gcf', 'lcm']
