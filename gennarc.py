from gen import *
from nds import narc, nclr
import os

ofile = None

FNAME = "narc"+FEXT

def printable(magic):
    ret = ""
    for c in magic:
        if ord(c) < 0x20:
            ret += "\\x%02X"%ord(c)
        else:
            ret += c
    return ret

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
            template.mkdir(os.path.dirname(ODIR+d))
            pfile = template.open(ODIR+d+FEXT, "w", "Pokemon %s NARC - %s"%(game.title(), d))
            pfile.write("<p><a href='%s%s'>NARC list</a></p>\n<table class='filelist'>\
<tr><td>File Number</td><td>File Magic</td><td>File Size</td></tr>\n"%("../"*len(d.strip("/").split("/")), FNAME))
            for j, f in enumerate(n.gmif.files):
                pfile.write("<tr><td>%i</td><td>%s</td><td>%i bytes</td></tr>\n"%(j, printable(f[:4]), len(f)))
            pfile.write("</table>\n")
            pfile.close()
            ofile.write("\t<tr><td><a href='narc%s'>%s</a></td><td>%i files</td></tr>\n"%(d+FEXT, d, n.btaf.getEntryNum()))
        else:
            f.close()
            ofile.write("\t<tr><td>%s</td><td>Not a NARC</td></tr>\n"%d)
            

for game in games:
    ODIR = STATIC_DIR+game+"/narc/"
    ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s NARC (Archive) Files"%game.title())
    ofile.write("""
<h2>Pokemon %s NARC (Archive) Files</h2>
<table class='filelist'>\n"""%game.title())
    C_DIR = DATA_DIR+game+"/fs"
    recursefs("")
    ofile.write("</table>")
    ofile.close()