
import os
import subprocess

from six.moves import input

from util.xorpad import xorstream

if os.name == "nt":
    binary = "bin/ctrtool.exe"
else:
    binary = "bin/ctrtool"


def dump(fname, directory, xorpad):
    subprocess.call([binary, '-p',
                     '--romfs', os.path.join(directory, 'romfs.bin'),
                     fname
                     ])
    with open(os.path.join(directory, 'ncch_header.bin'), 'wb') as header:
        with open(fname) as handle:
            handle.seek(0x4000)  # TODO: seek NCSD specified offset
            header.write(handle.read(512))
    xorstream(os.path.join(directory, 'romfs.bin'), xorpad,
              outname=os.path.join(directory, 'romfs.dec.bin'))
    subprocess.call([binary,
                     '--romfsdir', os.path.join(directory, 'fs'),
                     os.path.join(directory, 'romfs.dec.bin')
                     ])


def build(fname, directory):
    pass
