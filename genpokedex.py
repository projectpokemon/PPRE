from gen import *
from nds import narc, fieldgen
import struct

FNAME = "pokedex"+FEXT

for game in games:
    title = "Pokemon %s Pokedex/Personal Format"%game.title()
    ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", title)
    fieldgen.generateFormatHTML(dexfmt[game], title, ofile)
    ofile.close()
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", title)
    ofile.write("""
<h2>Pokemon %s Pokemon Data</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format</a></p>
"""%(game.title(), POKEDEX_FILE[game], FORMAT_SUBDIR, FNAME))
    fieldgen.makeHtmlEntries(dexfmt[game], 
        DATA_DIR+game+"/fs/"+POKEDEX_FILE[game], ofile)
    ofile.close()