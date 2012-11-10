from gen import *
import os, sys, struct
from PIL import Image

if "--dump-banner" in sys.argv:
    for game in games:
        os.system("./ndstool -x local/roms/%s.nds -t %s%s/banner.bin"%(game, DATA_DIR, game))
    
for game in games:
    banner = open(DATA_DIR+game+"/banner.bin", "rb")
    oname = STATIC_DIR+game+"/banner.png"
    banner.seek(32)
    im = Image.new("P", (32, 32))
    data = im.load()
    for i in range(4):
        for j in range(4):
            for k in range(8):
                for l in range(4):
                    p = ord(banner.read(1))
                    data[j*8+l*2+1, i*8+k] = p>>4
                    data[j*8+l*2, i*8+k] = p&0xF
    colors = []
    for i in range(16):
        p = struct.unpack("H", banner.read(2))[0]
        colors.extend([((p>>0)&0x1F)<<3, ((p>>5)&0x1F)<<3, ((p>>10)&0x1F)<<3])
    im.putpalette(colors)
    im.save(oname)