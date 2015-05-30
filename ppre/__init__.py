
import os
import sys

__all__ = ['PPRE_DIR', 'open_resource']

try:
    PPRE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
except NameError:
    PPRE_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))


def open_resource(*path, **kwargs):
    """Open a resource relative to PPRE's base directory

    *path : *string
        path arguments
    mode : string
        mode to open file as
    """
    mode = kwargs.get('mode', 'r')
    return open(os.path.join(PPRE_DIR, *path), mode=mode)
