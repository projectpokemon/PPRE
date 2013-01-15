from gen import *
from nds import narc
from nds.txt import gen4get, gen5get
import struct, array
import cStringIO as StringIO

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
            $container |= $string.pop() << $bit
            while $bit >= 9
                $bit -= 9
                $newstring.append($container&0x1FF)
                $container >>= 9
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
    
gen5alg = """
uint16 numblocks = read16()
uint16 numentries = read16()

uint32 filesize = read32()
uint32 zero = read32()

uint32 blockoffsets[numblocks]
uint32 tableoffsets[numblocks][numentries]
uint16 charcounts[numblocks][numentries]
uint16 textflags[numblocks][numentries]

string texts[numblocks][numentries]

for i from 1 to numblocks
    blockoffsets[i] = read32()
for i from 1 to numblocks
    seek(blockoffsets[i])
    uint32 blocksize = read32()
    for j from 1 to numentries
        tableoffsets[i][j] = read32()
        charcounts[i][j] = read16()
        textflags[i][j] = read16()
    for j from 1 to numentries
        $encchars = [0]
        $decchars = [0]
        $string = texts[i][j]
        seek(blockoffsets[i] + tableoffsets[i][j])
        for k from 1 to charcounts[i][j]
            $encchars.append(read16())
        $key = $encchars[-1]
        while $encchars
            $decchars.append($encchars.pop() ^ $key)
            $key = (($key>>3)|($key<<13))&0xFFFF
        while $decchars
            $char = $decchars.pop()
            if $char is 0xFFFF
                break
            else if $char == 0xFFFE
                $string += "\\n"
            else if $char == 0xF000
                $string += SPECIAL($char)
            else
                $string += unichr($char)
            
"""

def getlenfromlabel(x):
    maxlen = 0
    for text in x:
        l = int(text[0].split("_")[1].strip("cABCDEFGHIJKLMNOP"))
        if l > maxlen:
            maxlen = l
    return maxlen
textfmt = {
    "diamond":[gen4get, gen4alg, len],
    "platinum":[gen4get, gen4alg, len],
    "heartgold":[gen4get, gen4alg, len],
    "black":[gen5get, gen5alg, getlenfromlabel],
    "black2":[gen5get, gen5alg, getlenfromlabel],
}

for msg in [["msg", MSG_FILE, "Message/Text"], ["msg2", MSG_FILE2, "Script/Text"]]:
    FNAME = msg[0]+FEXT
    for game in games:
        if game not in msg[1]:
            continue
        gettext = textfmt[game][0]
        alg = textfmt[game][1]
        getlen = textfmt[game][2]
        ofile = template.open(STATIC_DIR+game+"/"+FORMAT_SUBDIR+FNAME, "w", "Pokemon %s %s Format"%(game.title(), msg[2]))
        ofile.write("<code style='white-space:pre;'>\n")
        for line in alg.split("\n"):
            ofile.write("%s\n"%line)
        ofile.write("</code>\n")
        ofile.close()
        n = narc.NARC(open(DATA_DIR+game+"/fs/"+msg[1][game], "rb").read())
        ofile = template.open(STATIC_DIR+game+"/"+FNAME, "w", "Pokemon %s %s Format"%(game.title(), msg[2]))
        ofile.write("""
<h2>Pokemon %s Message Data</h2>
<h3>%s - NARC Container</h3>
<p><a href='./%s%s'>Format/Algorithm</a></p>
<table>
<tr>
    <td>Index</td><td>Contents</td><td>Entries</td>
</tr>\n"""%(game.title(), msg[1][game], FORMAT_SUBDIR, FNAME))
        ODIR = STATIC_DIR+game+"/"+msg[0]+"/"
        if not os.path.exists(ODIR):
            os.mkdir(ODIR)
        for j, f in enumerate(n.gmif.files):
            texts = gettext(f) # [[num, text], [num, text]]
            ofile.write("<tr><td>%i</td><td><a href='%s/%i%s'>Text %i</a></td><td>%i</td></tr>\n"%(j, msg[0], j, FEXT, j, getlen(texts)))
            mfile = open(ODIR+str(j)+FEXT, "w")
            mfile.write("""
<h2>Pokemon %s Message File #%i</h2>
<h3>%s/%i - <a href="../%s%s">Message Formatted File</a></h3>
<p><a href="../%s">Message File Index</a></p>
"""%(game.title(), j, msg[1][game], j, FORMAT_SUBDIR, FNAME, FNAME))
            for k, text in enumerate(texts):
                mfile.write("<p><a href='#entry%i' name='entry%i'># %s</a> %s</p>\n"%(k, k, text[0], "<br>".join("<br>".join(text[1].encode("utf-8").split("\\n")).split("\\r"))))
            mfile.close()
        ofile.write("</table>\n")
        ofile.close()
    