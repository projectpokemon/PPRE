
import os
import subprocess

from six.moves import input

if os.name == "nt":
    binary = "bin/ctrtool.exe"
else:
    binary = "bin/ctrtool"


def dump(fname, directory):
    input('Hit enter')
    subprocess.call([binary,
                     '--romfsdir', os.path.join(directory, 'fs'),
                     os.path.join(directory, 'decrypted_romfs.bin')
                     ])


def build(fname, directory):
    pass
