import os, subprocess

if os.name == "nt":
    binary = "bin/xdelta3.exe"
else:
    binary = "bin/xdelta3"
    if not os.path.exists(binary):
        binary = "xdelta3"

def makePatch(patchname, fname1, fname2):
    subprocess.call([binary, "-e", "-s", fname1, fname2, patchname])
    
def applyPatch(patchname, fname1, fname2):
    subprocess.call([binary, "-d", "-s", fname1, patchname, fname2])
    