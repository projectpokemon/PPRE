import os, subprocess

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