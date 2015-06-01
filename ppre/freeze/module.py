""" Setup script to freeze a module with a main() as a CLI application

Invoke as `python -m ppre.freeze.module some/ppre/script.py <command>`
For creating windows executable, <command> should be bdist_msi.

Script should have a main() invoked when `__name__ == '__main__'`.
The script can optionally define a data_file_patterns list of globbed files to
include at the root of the packaged archive, eg
`data_file_patterns = ['data/defaults/*.csv']`

"""

import glob
import imp
import os
import sys

from cx_Freeze import setup, Executable

try:
    script = sys.argv.pop(1)
except:
    print('Usage: python -m ppre.freeze.module some/ppre/script.py <command>')
    exit(1)

data_file_targets = []
module = imp.load_source('__script__', script)
try:
    data_file_patterns = module.data_file_patterns
except AttributeError:
    pass
else:
    for data_file_pattern in data_file_patterns:
        for match in glob.iglob(data_file_pattern):
            if os.path.isdir(match):
                for base, dirs, files in os.walk(match):
                    for fname in files:
                        data_file_targets.append(os.path.join(base, fname))
            elif os.path.isfile(match):
                data_file_targets.append(match)


setup(
    executables=[Executable(script)],
    options={
        'build_exe': {
            'bundle_files': 1,
            'compressed': True,
        }
    },
    include_files=[data_file_targets]
)
