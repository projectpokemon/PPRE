from gen import *
from nds import narc
import struct

FNAME = "enc"+FEXT
GAMEFILE = ENC_FILE
datafmt = encfmt

for game in games:
    if not game in datafmt:
        continue
    fmt = datafmt[game].pop(0)
    fmtsize = struct.calcsize(fmt)
    ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", "Pokemon %s Encounter Format"%game.title())
    ofile.write("""
<h2>Pokemon %s Encounter Format</h2>
<p>Structure Size: %d bytes</p>
<table>
<tr><td>Offset</td><td>Length</td><td>Name</td></tr>
"""%(game.title(), fmtsize))
    ofs = 0
    """for i, entry in enumerate(datafmt[game]):
        ofile.write("<tr><td>%d</td><td>%d</td><td>%s</td></tr>\n"%(ofs, struct.calcsize(fmt[i]), entry))
        ofs += struct.calcsize(fmt[i])"""
    writefmt(ofile, fmt, datafmt[game])
    ofile.write("</table>\n")
    ofile.close()
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s Encounter Data"%game.title())
    ofile.write("""
<h2>Pokemon %s Encounters</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format</a></p>
<table>\n"""%(game.title(), GAMEFILE[game], FORMAT_SUBDIR, FNAME))
    n = narc.NARC(open(DATA_DIR+game+"/fs/"+GAMEFILE[game], "rb").read())
    for j, f in enumerate(n.gmif.files):
        ofile.write("\t<tr><td><h4>Location Id #%d</h4></td></tr>\n"%j)
        data = struct.unpack(fmt, f[:fmtsize])
        for i, entry in enumerate(datafmt[game]):
            if entry == "pad" and data[i]:
                print(j, data[i])
            ofile.write("\t<tr><td>%s</td><td>%d</td></tr>\n"%(entry, data[i]))
    ofile.write("</table>")
    ofile.close()