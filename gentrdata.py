from gen import *
from nds import narc
import struct

FNAME = "trdata"+FEXT

for game in games:
    fmt = trdatafmt[game].pop(0)
    fmtsize = struct.calcsize(fmt)
    ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", "Pokemon %s Trainer Data Format"%game.title())
    ofile.write("""
<h2>Pokemon %s Trainer Format</h2>
<p>Structure Size: %d bytes</p>
<table>
<tr><td>Offset</td><td>Length</td><td>Name</td></tr>
"""%(game.title(), fmtsize))
    ofs = 0
    for i, entry in enumerate(trdatafmt[game]):
        ofile.write("<tr><td>%d</td><td>%d</td><td>%s</td></tr>\n"%(ofs, struct.calcsize(fmt[i]), entry[0]))
        ofs += struct.calcsize(fmt[i])
    ofile.write("</table>\n")
    ofile.close()
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s Trainer Data"%game.title())
    ofile.write("""
<h2>Pokemon %s Trainers</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format</a></p>
<table>\n"""%(game.title(), TRDATA_FILE[game], FORMAT_SUBDIR, FNAME))
    n = narc.NARC(open(DATA_DIR+game+"/fs/"+TRDATA_FILE[game], "rb").read())
    for j, f in enumerate(n.gmif.files):
        ofile.write("\t<tr><td><h4>Trainer Id #%d</h4></td></tr>\n"%j)
        if len(f) < fmtsize:
            continue
        data = struct.unpack(fmt, f[:fmtsize])
        for i, entry in enumerate(trdatafmt[game]):
            ofile.write("\t<tr><td>%s</td><td>%d</td></tr>\n"%(entry[0], data[i]))
    ofile.write("</table>")
    ofile.close()