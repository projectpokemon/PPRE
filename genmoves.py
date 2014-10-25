from gen import *
from nds import narc
import struct

FNAME = "levelmoves"+FEXT

for game in games:
    fmt = movefmt[game].pop(0)
    ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", "Pokemon %s Level-Up Move Format"%game.title())
    ofile.write("""
<h2>Pokemon %s Level-Up Move Format</h2>
<p>Structure Size: %d bytes</p>
<p>Structures continue until 0xFFFF is reached (Maximum of 20 entries per file).</p>
<table>
<tr><td>Bits</td><td>Name</td></tr>
"""%(game.title(), struct.calcsize(fmt)))
    for i, entry in enumerate(movefmt[game]):
        ofile.write("<tr><td>%d-%d</td><td>%s</td></tr>"%(entry[1], entry[2], entry[0]))
    ofile.write("</table>\n")
    ofile.close()
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s Level-Up Move Data"%game.title())
    ofile.write("""
<h2>Pokemon %s Level-Up Moves</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format</a></p>
<table>\n"""%(game.title(), LEVELMOVE_FILE[game], FORMAT_SUBDIR, FNAME))
    n = narc.NARC(open(DATA_DIR+game+"/fs/"+LEVELMOVE_FILE[game], "rb").read())
    for j, f in enumerate(n.gmif.files):
        ofile.write("\t<tr><td><h4>Pokemon Id #%d</h4></td></tr>\n"%j)
        while 1:
            data = struct.unpack(fmt, f[:struct.calcsize(fmt)])
            if data[0]&0xFFFF == 0xffff:
                ofile.write("\t<tr><td colspan='2'>%d</td></tr>\n"%(data[0]))
                break
            for i, entry in enumerate(movefmt[game]):
                ofile.write("\t<tr><td>%s</td><td>%d</td></tr>\n"%(entry[0], (data[0]>>entry[1])&entry[3]))
            f = f[struct.calcsize(fmt):]
    ofile.write("</table>")
    ofile.close()