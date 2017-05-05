import struct
import narc

def getFieldsByString(datafmt, f):
    ret = []
    size = struct.calcsize(datafmt[0])
    vals = list(struct.unpack(datafmt[0], f[:size]))
    for d in datafmt[1:]:
        ret.append([d[0], vals.pop(0)])
    return ret
        
def getEntries(datafmt, fname):
    n = narc.NARC(open(fname, "rb").read())
    ret = []
    for j, f in enumerate(n.gmif.files):
        ret.append(getFieldsByString(datafmt, f))
    return ret
    
def generateFormatHTML(datafmt, title, ofile):
    fmt = datafmt[0]
    size = struct.calcsize(fmt)
    ofile.write("""
<h2>%s</h2>
<p>Structure Size: %d bytes</p>\n<table>\n"""%(title, size))
    ofs = 0
    for i, entry in enumerate(datafmt[1:]):
        ofile.write("<tr><td>%d</td><td>%d</td><td>%s</td></tr>"%(ofs, struct.calcsize(fmt[i]), entry[0]))
        ofs += struct.calcsize(fmt[i])
    ofile.write("</table>\n")
    
def defaultSeparator(i):
    return "<tr><th colspan='2'><a href='#entry-%i' name='entry-%i'># %i</a></th></tr>"%(i, i, i)

def makeHtmlEntries(datafmt, fname, ofile, separator=defaultSeparator):
    entries = getEntries(datafmt, fname)
    ofile.write("<table class='datatable'>")
    for i, entry in enumerate(entries):
        ofile.write(separator(i))
        for field in entry:
            line = ""
            if isinstance(field[1], basestring):
                line = "\n<tr><td>%s</td><td>%s</td></tr>\n" % (field[0], field[1].strip())
            else:
                line = "\n<tr><td>%s</td><td>%i</td></tr>\n" % (field[0], field[1])
            ofile.write(line)
    ofile.write("</table>")