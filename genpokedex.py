from gen import *
from nds import narc
import struct

FNAME = "pokedex"+FEXT

for game in games:
    fmt = dexfmt[game].pop(0)
    ofile = open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w")
    ofile.write("""
<h2>Pokemon %s Pokedex/Personal Format</h2>
<p>Structure Size: %d bytes</p>\n<table>\n"""%(game.title(), struct.calcsize(fmt)))
    ofs = 0
    for i, entry in enumerate(dexfmt[game]):
        ofile.write("<tr><td>%d</td><td>%d</td><td>%s</td></tr>"%(ofs, struct.calcsize(fmt[i]), entry[0]))
        ofs += struct.calcsize(fmt[i])
    ofile.write("</table>\n")
    ofile.close()
    ofile = open(STATIC_DIR+game+"/"+FNAME, "w")
    ofile.write("""
<h2>Pokemon %s Pokemon Data</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format</a></p>
<table>\n"""%(game.title(), POKEDEX_FILE[game], FORMAT_SUBDIR, FNAME))
    n = narc.NARC(open(DATA_DIR+game+"/fs/"+POKEDEX_FILE[game], "rb").read())
    for j, f in enumerate(n.gmif.files):
        ofile.write("\t<tr><td><h4>Pokemon Id #%d</h4></td></tr>\n"%j)
        dexdata = struct.unpack(fmt, f[:struct.calcsize(fmt)])
        for i, entry in enumerate(dexfmt[game]):
            if entry[0] == "pad" and dexdata[i]:
                print(j, dexdata[i])
            ofile.write("\t<tr><td>%s</td><td>%d</td></tr>\n"%(entry[0], dexdata[i]))
    ofile.write("</table>")
    ofile.close()