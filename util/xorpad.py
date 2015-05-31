
import ctypes
from itertools import izip
import os

BLOCK_READ_SIZE = 0x100000


def xorstream(fname1, fname2, outname):
    """Open two files and write their xorstream to a third file immediately"""
    with open(fname1) as handle1, open(fname2) as handle2,\
            open(outname, 'wb') as out:
        moredata = True
        while moredata:
            data1 = handle1.read(BLOCK_READ_SIZE)
            data2 = handle2.read(BLOCK_READ_SIZE)
            if len(data1) < BLOCK_READ_SIZE or len(data2) < BLOCK_READ_SIZE:
                moredata = False
            buffer = ''
            for ch1, ch2 in izip(data1, data2):
                buffer += chr(ord(ch1) ^ ord(ch2))
            out.write(buffer)


class FILE(ctypes.Structure):
    pass
FILE_P = ctypes.POINTER(FILE)
PyFile_AsFile = ctypes.pythonapi.PyFile_AsFile
PyFile_AsFile.argtypes = [ctypes.py_object]
PyFile_AsFile.restype = FILE_P


try:
    xorpad_ = ctypes.cdll.LoadLibrary(os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'xorpad_.so')))
    xorpad_.xorstream.argtypes = [FILE_P, FILE_P, FILE_P]

    def xorstream(fname1, fname2, outname):
        """Open two files and write their xorstream to a third file immediately

        This uses the C implementation (Linux only, at the moment)
        """
        with open(fname1) as handle1, open(fname2) as handle2,\
                open(outname, 'wb') as out:
            xorpad_.xorstream(PyFile_AsFile(handle1), PyFile_AsFile(handle2),
                              PyFile_AsFile(out))
except:
    pass


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 4:
        print('Usage: {0} <file 1> <file 2> <out file>'.format(sys.argv[0]))
    xorstream(sys.argv[1], sys.argv[2], sys.argv[3])
