from gen import *

ofile = None

def recursefs(d):
    desc = ""
    if d in fs[game]:
        desc = fs[game][d]
    elif os.path.isdir(C_DIR+d):
        desc = "Directory"
    ofile.write("\t<tr><td>%s</td><td>%s</td></tr>\n"%(d, desc))
    if os.path.isdir(C_DIR+d):
        for f in sorted(os.listdir(C_DIR+d)):
            recursefs(d+"/"+f)

for game in games:
    ofile = template.open(STATIC_DIR+game+"/filelist"+FEXT, "w", "Pokemon %s Filelist"%game.title())
    ofile.write("""
<h2>Pokemon %s Internal Filelist</h2>
<table class='filelist'>\n"""%game.title())
    C_DIR = DATA_DIR+game+"/fs"
    recursefs("")
    ofile.write("</table>")
    ofile.close()