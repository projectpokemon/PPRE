
import os, subprocess

from compat import input

if os.name == "nt":
    binary = "bin/ndstool.exe"
else:
    binary = "bin/ndstool"
    
def dump(f, d):
    subprocess.call([binary, "-x", f, "-7", d+"/arm7.bin", 
        "-y7", d+"/overarm7.bin", "-9", d+"/arm9.bin", "-y9", d+"/overarm9.bin",
        "-y", d+"/overlays", "-t", d+"/banner.bin", "-h", d+"/header.bin",
        "-d", d+"/fs"])

def build(f, d):
    subprocess.call([binary, "-c", f, "-7", d+"/arm7.bin", 
        "-y7", d+"/overarm7.bin", "-9", d+"/arm9.bin", "-y9", d+"/overarm9.bin",
        "-y", d+"/overlays", "-t", d+"/banner.bin", "-h", d+"/header.bin",
        "-d", d+"/fs"])


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



