from gen import *
from nds import narc
import struct

FNAME = "exprate"+FEXT

for game in games:
    fmt = "I"*101
    ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", "Pokemon %s Experience/Growth Table Format"%game.title())
    ofile.write("""
<h2>Pokemon %s Experience/Growth Table Format</h2>
<p>Structure Size: %d bytes</p>\n<p>4 bytes * 101 entries</p>\n"""%(game.title(), struct.calcsize(fmt)))
    ofile.close()
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s Experience/Growth Table Data"%game.title())
    ofile.write("""
<h2>Pokemon %s Experience Table</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format</a></p>
<table>\n"""%(game.title(), EXPRATE_FILE[game], FORMAT_SUBDIR, FNAME))
    n = narc.NARC(open(DATA_DIR+game+"/fs/"+EXPRATE_FILE[game], "rb").read())
    for j, f in enumerate(n.gmif.files):
        ofile.write("\t<tr><td><h4>Growth Id #%d</h4></td></tr>\n"%j)
        expdata = struct.unpack(fmt, f)
        for i, entry in enumerate(expdata):
            ofile.write("\t<tr><td>Level %s</td><td>%d Exp</td></tr>\n"%(i, entry))
    ofile.write("</table>")
    ofile.close()