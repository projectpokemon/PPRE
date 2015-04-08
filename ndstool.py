
import os
import subprocess

from compat import input

if os.name == 'nt':
    binary = os.path.join(os.path.dirname(__file__), 'bin', 'ndstool.exe')
else:
    binary = os.path.join(os.path.dirname(__file__), 'bin', 'ndstool')


def dump(fname, directory):
    subprocess.call([binary, '-x', fname,
                     '-7', os.path.join(directory, 'arm7.bin'),
                     '-y7', os.path.join(directory, 'overarm7.bin'),
                     '-9', os.path.join(directory, 'arm9.bin'),
                     '-y9', os.path.join(directory, 'overarm9.bin'),
                     '-y', os.path.join(directory, 'overlays'),
                     '-t', os.path.join(directory, 'banner.bin'),
                     '-h', os.path.join(directory, 'header.bin'),
                     '-d', os.path.join(directory, 'fs')
                     ])


def build(fname, directory):
    arm9 = os.path.join(directory, 'arm9.dec.bin')
    try:
        if not os.path.getsize(arm9):
            raise OSError()
    except OSError:
        arm9 = os.path.join(directory, 'arm9.bin')
    subprocess.call([binary, '-c', fname,
                     '-7', os.path.join(directory, 'arm7.bin'),
                     '-y7', os.path.join(directory, 'overarm7.bin'),
                     '-9', arm9,
                     '-y9', os.path.join(directory, 'overarm9.bin'),
                     '-y', os.path.join(directory, 'overlays'),
                     '-t', os.path.join(directory, 'banner.bin'),
                     '-h', os.path.join(directory, 'header.bin'),
                     '-d', os.path.join(directory, 'fs')
                     ])


if __name__ == '__main__':
    import sys

    try:
        command = sys.argv[1].lower()
        if command not in ('build', 'dump'):
            raise ValueError
        options = []
        argc = 2
        for arg in sys.argv[argc:]:
            if arg[0] == '-':
                argc += 1
                if arg[1] == '-':
                    break
                options.append(arg)
            else:
                break
        rom = sys.argv[argc]
        directory = sys.argv[argc+1]
        argc += 2
        if len(sys.argv) != argc:
            raise ValueError
    except:
        print("""Usage: %s COMMAND [options] ROM DIRECTORY

    COMMAND
        build
            Creates a ROM from the specified directory

        dump
            Dumps ROM to specified directory

    OPTIONS
        -y --assume-yes
            Overwrite target directory automatically when extracting.
            Overwrite ROM automatically when building
        --
            No further arguments. This is required when ROM starts with
            a - character.
        """ % sys.argv[0])
        exit()
    if command == 'build':
        if os.path.exists(rom) and '-y' not in options and \
                '--assume-yes' not in options:
            if input('Do you want to overwrite %s? [y/n] ' % rom).\
                    lower() != 'y':
                print('Aborted building new ROM')
                exit()
        build(rom, directory)
    elif command == 'dump':
        if os.path.exists(directory) and '-y' not in options and \
                '--assume-yes' not in options:
            if input('Do you want to overwrite %s? [y/n] ' % directory).\
                    lower() != 'y':
                print('Aborted dumping ROM')
                exit()
        try:
            os.mkdir(directory)
        except OSError:
            pass
        dump(rom, directory)



