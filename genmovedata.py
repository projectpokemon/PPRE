from gen import *
from nds import narc, fieldgen
import struct

FNAME = "movedata"+FEXT

for game in games:
    title = "Pokemon %s Move Data Format"%game.title()
    ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", title)
    fieldgen.generateFormatHTML(movedatafmt[game], title, ofile)
    ofile.close()
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", title)
    ofile.write("""
<h2>Pokemon %s Move Data</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format</a></p>
"""%(game.title(), MOVEDATA_FILE[game], FORMAT_SUBDIR, FNAME))
    fieldgen.makeHtmlEntries(movedatafmt[game], 
        DATA_DIR+game+"/fs/"+MOVEDATA_FILE[game], ofile)
    ofile.close() 