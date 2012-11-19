from gen import *
from nds import narc, ncgr
import os

ofile = None

FNAME = "ncgr"+FEXT

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
            dirname = os.path.dirname(ODIR+d)
            for j, f in enumerate(n.gmif.files):
                if f[:4] == "RGCN":
                    count += 1
                    graphic = ncgr.NCGR(f)
                    if not pfile:
                        template.mkdir(dirname)
                        pfile = template.open(ODIR+d+FEXT, "w", "Pokemon %s NCGR - %s"%(game.title(), d))
                        pfile.write("<p><a href='%s%s'>RGCN list</a></p>\n"%("../"*len(d.strip("/").split("/")), FNAME))
                    pfile.write("<p>File %i: %ix%i</p>"%(j, graphic.char.width, graphic.char.height))
                    pfile.write("<p><img src='%i.png' alt='%s %i RGCN'></p>\n"%(j, d, j))
                    graphic.toImage().save("%s/%i.png"%(dirname, j))
                    del graphic
            if pfile:
                pfile.close()
        else:
            f.close()
        if count:
            ofile.write("\t<tr><td><a href='ncgr%s'>%s</a></td><td>%i files</td></tr>\n"%(d+FEXT, d, count))
        else:
            ofile.write("\t<tr><td>%s</td><td>0 files</td></tr>\n"%d)
            

for game in games:
    ODIR = STATIC_DIR+game+"/ncgr/"
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s NCGR (Graphics) Files"%game.title())
    ofile.write("""
<h2>Pokemon %s NCGR (Graphics) Files</h2>
<table class='filelist'>\n"""%game.title())
    C_DIR = DATA_DIR+game+"/fs"
    recursefs("")
    ofile.write("</table>")
    ofile.close()