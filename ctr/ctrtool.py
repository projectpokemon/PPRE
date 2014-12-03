
import os
import subprocess

from six.moves import input

from util.xorpad import xorstream

if os.name == "nt":
    binary = "bin/ctrtool.exe"
else:
    binary = "bin/ctrtool"


def dump(fname, directory):
    input('Hit enter')
    subprocess.call([binary, '-p',
                     '--romfs', os.path.join(directory, 'romfs.bin'),
                     os.path.join(fname)
                     ])
    xorstream(os.path.join(directory, 'romfs.bin'),
              os.path.join(directory, 'romfs.xorpad'),
              outname=os.path.join(directory, 'romfs.dec.bin'))
    subprocess.call([binary,
                     '--romfsdir', os.path.join(directory, 'fs'),
                     os.path.join(directory, 'romfs.dec.bin')
                     ])


def build(fname, directory):
    pass
