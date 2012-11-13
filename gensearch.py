from gen import *
from nds import narc
import struct

FNAME = "search"+FEXT

for game in games:
    if game not in ZUKAN_FILE:
        continue
    ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", "Pokemon %s Pokedex Search Format"%game.title())
    ofile.write("""
<h2>Pokemon %s Pokedex Search</h2>\n"""%(game.title()))
    for i in sorted(searchfiles[game]):
        ofile.write("<h4>File #%i - %s</h4>\n"%(i, searchfiles[game][i][0]))
        for j, entry in enumerate(searchfiles[game][i][2]):
            ofile.write("<p>%s - %i bytes * POKEMON</p>\n"%(entry, struct.calcsize(searchfiles[game][i][1][j])))
    ofile.close()
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s Pokedex Search Data"%game.title())
    ofile.write("""
<h2>Pokemon %s Pokedex Search Lookup</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format</a></p>
<table>
"""%(game.title(), ZUKAN_FILE[game], FORMAT_SUBDIR, FNAME))
    n = narc.NARC(open(DATA_DIR+game+"/fs/"+ZUKAN_FILE[game], "rb").read())
    i = 0
    for j, f in enumerate(n.gmif.files):
        if j in searchfiles[game]:
            fmt = searchfiles[game][j][1]
            datafmt = searchfiles[game][j][2]
            name = searchfiles[game][j][0]
        else:
            fmt = "H"
            datafmt = ["natid?"]
            name = "undocumented/unknown"
        fmtsize = struct.calcsize(fmt)
        ofile.write("<h4>File Id #%d - %s</h4>\n"%(j, name))
        k = 0
        while len(f) >= fmtsize:
            data = struct.unpack(fmt, f[:fmtsize])
            for i, entry in enumerate(datafmt):
                ofile.write("\t<p>%i: %i %s</p>\n"%(k, data[i], entry))
            f = f[fmtsize:]
            k += 1
    ofile.write("</table>")
    ofile.close()