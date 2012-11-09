from gen import *
from nds import narc
import struct, array
import cStringIO as StringIO
import unicodeparser

FNAME = "msg"+FEXT 

gen4alg = """
uint16 num = read16()
uint16 seed = read16()

uint32 offsets[num]
uint32 sizes[num]

uint16 binarystrings[num][$size]

string texts[num]

/* generate offsets and sizes */
for i from 1 to num
    $key = ((seed*i*0x2FD)&0xFFFF) | ((seed*i*0x2FD0000)&0xFFFF0000)
    offsets[i] = read32() ^ $key
    sizes[i] = read32() ^ $key

for i from 1 to num
    /* temporary references */
    $offset = offsets[i]
    $size = sizes[i]
    $string = binarystrings[i]
    $key = (0x91BD3*i)&0xFFFF
    $text = texts[i]
    
    seek($offset)
    /* decrypt strings */
    for j from 1 to $size
        $string[j] = read16() ^ $key
        $key = ($key+0x493D)&0xFFFF
        
    if $string[1] is 0xF100
        /* decompress string: characters are stored in 9 bits instead of 16 */
        $newstring = [0]
        $string.pop()
        $container = 0
        $bit = 0
        while $string
            while $string and $container < 0x200
                $container |= ($string.pop() << $bit)
                $bit += 9
            $newstring.append($container&0x1FF)
            $container >>= 9
            $bit -= 9
        $string = $newstring
        $size = $newstring.size
    $text = ""
    while $string
        int16 $char = $string.pop()
        if $char is -1
            break
        else if $char is -2
            $count = $string.pop()
            $args = [0]
            for k from 1 $count
                $args.append($string.pop())
            /* TEXT_VARIABLE is a function to come up with the value based on $args */
            $text += TEXT_VARIABLE($args)
        else
            /* SYMBOLS is a list of symbols that each character corresponds to */
            $text += SYMBOLS[$char]
            

"""

class binaryreader:
    def __init__(self, string):
        self.s = array.array('H',string)
        self.ofs = 0
        self.ReadUInt16 = self.read16
        self.ReadUInt32 = self.read32
        self.Seek = self.seek
    def read16(self):
        ret = self.s[self.ofs]
        self.ofs += 1
        return ret
    def read32(self):
        ret = self.s[self.ofs] | (self.s[self.ofs+1]<<16)
        self.ofs += 2
        return ret
    def seek(self, ofs):
        self.ofs = ofs>>1
        
def gen4get(f):
    texts = []
    reader = binaryreader(f)
    
    num = reader.read16()
    seed = reader.read16()
    offsets = []
    sizes = []
    for i in range(num):
        tmp = ((((seed*0x2FD)&0xFFFF)*(i+1))&0xFFFF)
        key = tmp | (tmp << 16)
        offsets.append(reader.read32() ^ key)
        sizes.append(reader.read32() ^ key)
    for i in range(num):
        offset = offsets[i]
        size = sizes[i]
        key = (0x91BD3*(i+1))&0xFFFF
        string = []
        for j in range(size):
            string.append(reader.read16() ^ key)
            key = (key+0x493D)&0xFFFF
        if string[0] == 0xF100:
            string.pop() # TODO: decompress
        text = ""
        while string:
            char = string.pop(0)
            if char == 0xFFFF:
                break
            if char == 0xFFFE:
                try:
                    kind = string.pop(0)
                    count = string.pop(0)
                    text += "VAR({"
                    args = [kind, count]
                    for k in range(count):
                        args.append(string.pop())
                except IndexError:
                    break
                text += ",".join(map(str, args))
                text += "})"
            else:
                try:
                    text += unicodeparser.tb[char]
                except:
                    text += "\\x%04X"%char
        texts.append([str(i), text])
    return texts
    
def gen5get(f):
    texts = []
    reader = binaryreader(f)
    
    numblocks = reader.read16()
    numentries = reader.read16()
    size0 = reader.read32()
    unk0 = reader.read32()
    blockoffsets = []
    for i in range(numblocks):
        blockoffsets.append(reader.read32())
    for i in range(numblocks):
        reader.seek(blockoffsets[i])
        size = reader.read32()
        tableoffsets = []
        charcounts = []
        unknowns = []
        for j in range(numentries):
            tableoffsets.append(reader.read32())
            charcounts.append(reader.read16())
            unknowns.append(reader.read16())
        for j in range(numentries):
            encchars = []
            text = ""
            reader.seek(blockoffsets[i]+tableoffsets[j])
            for k in range(charcounts[j]):
                encchars.append(reader.read16())
            key = encchars[len(encchars)-1]^0xFFFF
            decchars = []
            while encchars:
                char = encchars.pop() ^ key
                key = ((key>>3)|(key<<13))&0xFFFF
                decchars.append(char)
            #if decchars[0] == 0xF100:
            #    decchars.pop(0) #TODO: fill in
            while decchars:
                c = decchars.pop()
                if c == 0xFFFF:
                    break
                elif c == 0xFFFE:
                    text += "\\n"
                elif c < 20 or c > 0xFFF0:
                    text += "\\x%04X"%c
                else:
                    text += unichr(c)
            texts.append(["%i_%i"%(i, j), text])
    return texts

def getlenfromlabel(x):
    maxlen = 0
    for text in x:
        l = int(text[0].split("_")[1])
        if l > maxlen:
            maxlen = l
    return maxlen
textfmt = {
    "diamond":[gen4get, gen4alg, len],
    "platinum":[gen4get, gen4alg, len],
    "heartgold":[gen4get, gen4alg, len],
    "black":[gen5get, "", getlenfromlabel],
    "black2":[gen5get, "", getlenfromlabel],
}

for game in games:
    gettext = textfmt[game][0]
    alg = textfmt[game][1]
    getlen = textfmt[game][2]
    ofile = open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w")
    ofile.write("<code style='white-space:pre;'>\n")
    for line in alg.split("\n"):
        ofile.write("%s\n"%line)
    ofile.write("</code>\n")
    ofile.close()
    n = narc.NARC(open(DATA_DIR+game+"/fs/"+MSG_FILE[game], "rb").read())
    ofile = open(STATIC_DIR+game+"/"+FNAME, "w")
    ofile.write("""
<h2>Pokemon %s Message Data</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format/Algorithm</a></p>
<table>
<tr>
    <td>Index</td><td>Contents</td><td>Entries</td>
</tr>\n"""%(game.title(), MSG_FILE[game], FORMAT_SUBDIR, FNAME))
    ODIR = STATIC_DIR+game+"/msg/"
    if not os.path.exists(ODIR):
        os.mkdir(ODIR)
    for j, f in enumerate(n.gmif.files):
        texts = gettext(f) # [[num, text], [num, text]]
        ofile.write("<tr><td>%i</td><td><a href='msg/%i%s'>Text %i</a></td><td>%i</td></tr>\n"%(j, j, FEXT, j, getlen(texts)))
        mfile = open(ODIR+str(j)+FEXT, "w")
        mfile.write("""
<h2>Pokemon %s Message File #%i</h2>
<h3>%s/%i - <a href="../%s%s">Message Formatted File</a></h3>
<p><a href="../%s">Message File Index</a></p>
"""%(game.title(), j, MSG_FILE[game], j, FORMAT_SUBDIR, FNAME, FNAME))
        for k, text in enumerate(texts):
            mfile.write("<p><a href='#entry%i' name='entry%i'># %s</a> %s</p>\n"%(k, k, text[0], "<br>".join("<br>".join(text[1].encode("utf-8").split("\\n")).split("\\r"))))
        mfile.close()
    ofile.write("</table>\n")
    ofile.close()
    
