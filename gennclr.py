from gen import *
from nds import narc, nclr
import os

ofile = None

FNAME = "nclr"+FEXT

def recursefs(d):
    if os.path.isdir(C_DIR+d):
        for f in sorted(os.listdir(C_DIR+d)):
            recursefs(d+"/"+f)
    else:
        f = open(C_DIR+d, "rb")
        count = 0
        if f.read(4) == "NARC":
            f.seek(0)
            n = narc.NARC(f.read())
            f.close()
            pfile = None
            for j, f in enumerate(n.gmif.files):
                if f[:4] == "RLCN":
                    count += 1
                    clr = nclr.NCLR(f)
                    if not pfile:
                        template.mkdir(os.path.dirname(ODIR+d))
                        pfile = template.open(ODIR+d+FEXT, "w", "Pokemon %s NCLR - %s"%(game.title(), d))
                        pfile.write("<p><a href='%s%s'>RLCN list</a></p>"%("../"*len(d.strip("/").split("/")), FNAME))
                    pfile.write("<p>File %i: "%j)
                    for k, c in enumerate(clr.pltt.colors):
                        pfile.write("<span style='background-color: #%02X%02X%02X;'>%i</span>"%(c[0], c[1], c[2], k))
                    pfile.write("</p>\n")
            if pfile:
                pfile.close()
        else:
            f.close()
        if count:
            ofile.write("\t<tr><td><a href='nclr%s'>%s</a></td><td>%i files</td></tr>\n"%(d+FEXT, d, count))
        else:
            ofile.write("\t<tr><td>%s</td><td>0 files</td></tr>\n"%d)
            

for game in games:
    ODIR = STATIC_DIR+game+"/nclr/"
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s NCLR (Palette) Files"%game.title())
    ofile.write("""
<h2>Pokemon %s NCLR (Palette) Files</h2>
<table class='filelist'>\n"""%game.title())
    C_DIR = DATA_DIR+game+"/fs"
    recursefs("")
    ofile.write("</table>")
    ofile.close()