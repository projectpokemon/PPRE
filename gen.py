#!/usr/bin/env python
import os, sys
import struct
import template
from nds.fmt import *
from nds.files import *

allowed_games = ["diamond", "platinum", "heartgold", "black", "black2"]
EXT = "php"
DATA_DIR = "local/data/"
STATIC_DIR = "static/"
FORMAT_SUBDIR = "formats/"
genindex = False
games = []

args = sys.argv[1:]
while args:
    a = args.pop(0)
    if a == "--help":
        print("""Usage: %s [Options] [Game1 [Game2 [...]]]
If game is left blank, all games will be processed.

Options:
--gen-index         Generate index files.
--ext <extension>   Use <extension> for newly created files.
--help              Show this help, then exit.

Valid Games:
%s
"""%(sys.argv[0], ", ".join(allowed_games)))
        exit()
    if a == "--gen-index":
        genindex = True
        continue
    if a == "--ext":
        EXT = args.pop(0)
        continue
    if a in allowed_games:
        games.append(a)
if not games:
    games = allowed_games
FEXT = "."+EXT

struct_name = {"B": "UInt8", "H":"UInt16", "I":"UInt32"}

fs = getFSHTML(FEXT)

for game in games:
    if not os.path.exists(STATIC_DIR+game):
        os.makedirs(STATIC_DIR+game)
    if not os.path.exists(STATIC_DIR+game+"/formats"):
        os.makedirs(STATIC_DIR+game+"/formats")
    if genindex:
        template.idxfile(STATIC_DIR+game+"/index"+FEXT, "w", "Pokemon "+game.title()).close()
        template.idxfile(STATIC_DIR+game+"/formats/index"+FEXT, "w", "Pokemon "+game.title()+" Formats").close()
        
def writefmt(ofile, fmt, datafmt):
    ofs = 0
    padding = 0
    i = 0
    fmt = list(fmt)
    while fmt:
        padding = 0
        while fmt[0] in ('X', 'x'):
            fmt = fmt[1:]
            if not fmt:
                break
            padding += 1
        if padding:
            ofile.write("<tr><td>%d</td><td>%d</td><td>[padding]</td></tr>\n"%(ofs, padding))
            ofs += padding
        if not fmt:
            break
        ofile.write("<tr><td>%d</td><td>%d</td><td>%s</td></tr>\n"%(ofs, struct.calcsize(fmt[0]), datafmt[i]))
        ofs += struct.calcsize(fmt[0])
        fmt = fmt[1:]
        i += 1
        
if __name__ == "__main__":
    import genbaseevo, genenc, genevo, genexprate, genmoves, genpokedex, gentrdata, gentxt, gensearch
    import gennarc, gennclr
    import genfilelist