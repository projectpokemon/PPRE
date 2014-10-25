from gen import *
from nds import narc
import struct

FNAME = "evo"+FEXT

for game in games:
    fmt = evofmt[game].pop(0)
    ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", "Pokemon %s Evolution Format"%game.title())
    ofile.write("""
<h2>Pokemon %s Evolution Format</h2>
<p>Structure Size: %d bytes</p>
<table>
<tr><td>Offset</td><td>Byte Size</td><td>Name</td></tr>
"""%(game.title(), struct.calcsize(fmt)))
    ofs = 0
    for i, entry in enumerate(evofmt[game]):
        ofile.write("<tr><td>%d</td><td>%d</td><td>%s</td></tr>"%(ofs, struct.calcsize(fmt[i]), entry[0]))
        ofs += struct.calcsize(fmt[i])
    ofile.write("</table>\n")
    ofile.close()
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s Evolution Data"%game.title())
    ofile.write("""
<h2>Pokemon %s Evolutions</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format</a></p>
<table>\n"""%(game.title(), EVO_FILE[game], FORMAT_SUBDIR, FNAME))
    n = narc.NARC(open(DATA_DIR+game+"/fs/"+EVO_FILE[game], "rb").read())
    for j, f in enumerate(n.gmif.files):
        ofile.write("\t<tr><td><h4>Evolution Id #%d</h4></td></tr>\n"%j)
        evodata = struct.unpack(fmt, f)
        for i, entry in enumerate(evofmt[game]):
            ofile.write("\t<tr><td>%s</td><td>%d</td></tr>\n"%(entry[0], evodata[i]))
    ofile.write("</table>")
    ofile.close()