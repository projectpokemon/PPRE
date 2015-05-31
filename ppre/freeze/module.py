""" Setup script to freeze a module with a main() as a CLI application

Invoke as `python -m ppre.freeze.module some/ppre/script.py py2exe`

"""

import sys

from distutils.core import setup

try:
    script = sys.argv.pop(1)
except:
    print('Usage: python -m ppre.freeze.module some/ppre/script.py py2exe')
    exit(1)

setup(console=[script])
