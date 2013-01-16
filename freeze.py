import sys

sys.argv = ["freeze.py", "py2exe"]

from distutils.core import setup
import py2exe

setup(windows=[{"script" : "ppre.py"}],
      options={"py2exe" : {"includes" : ["sip"], "bundle_files":1}},
      zipfile=None) 
