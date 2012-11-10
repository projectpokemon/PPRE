from gen import *
from nds import narc
import struct

FNAME = "baseevo"+FEXT

for game in games:
    if game not in BASEEVO_FILE:
        continue
    fmt = "H"
    fmtsize = struct.calcsize(fmt)
    ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", "Pokemon %s Base Evolution/Baby Lookup Format"%game.title())
    ofile.write("""
<h2>Pokemon %s Base Evolution/Baby Lookup</h2>
<p>Structure Size: %d bytes</p>\n<p>2 bytes * POKEMON</p>\n"""%(game.title(), fmtsize))
    ofile.close()
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s Base Evolution/Baby Lookup Data"%game.title())
    ofile.write("""
<h2>Pokemon %s Base Evolution/Baby Lookup</h2>
<h3>%s - Raw Container</h3>
<p><a href='./%s%s'>Format</a></p>
<table>
<tr><td>Pokemon</td><td>Base Evolution/Baby</td></tr>
"""%(game.title(), BASEEVO_FILE[game], FORMAT_SUBDIR, FNAME))
    f = open(DATA_DIR+game+"/fs/"+BASEEVO_FILE[game], "rb").read()
    i = 0
    while f:
        data = struct.unpack(fmt, f[:fmtsize])
        ofile.write("\t<tr><td>%d</td><td>%d</td></tr>\n"%(i, data[0]))
        f = f[fmtsize:]
        i += 1
    ofile.write("</table>")
    ofile.close()