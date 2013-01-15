import narc
import struct, re
import cStringIO as StringIO
import unicodeparser
from binary16 import binaryreader, binarywriter

usedflags = "c"

def sortTextKeys(a, b):
    a1 = int(a[0].split("_")[1].strip(usedflags))
    b1 = int(b[0].split("_")[1].strip(usedflags))
    if a1 > b1:
        return 1
    if b1 > a1:
        return -1
    if a[0].split("_")[0].lower() == "comment":
        return -1
    return cmp(a[0], b[0])
    
def gen4get(f):
    texts = []
    reader = binaryreader(f)
    
    num = reader.read16()
    seed = reader.read16()
    hasComments = False
    if seed & 0xFF == 0xFF: # PPRE Seed
        if seed & 0x100:
            hasComments = True
    offsets = []
    sizes = []
    for i in range(num):
        tmp = ((((seed*0x2FD)&0xFFFF)*(i+1))&0xFFFF)
        key = tmp | (tmp << 16)
        offsets.append(reader.read32() ^ key)
        sizes.append(reader.read32() ^ key)
    if hasComments:
        tmp = ((((seed*0x2FD)&0xFFFF)*(i+1))&0xFFFF)
        key = tmp | (tmp << 16)
        commentOfs = reader.read32() ^ key
        term = reader.read32() ^ key
        if term != 0xFFFF:
            print("Erroneous comment offset terminator: %X"%term)
    for i in range(num):
        reader.seek(offsets[i])
        compressed = False
        offset = offsets[i]
        size = sizes[i]
        key = (0x91BD3*(i+1))&0xFFFF
        string = []
        for j in range(size):
            string.append(reader.read16() ^ key)
            key = (key+0x493D)&0xFFFF
        if string[0] == 0xF100:
            compressed = True
            string.pop(0)
            newstring = []
            container = 0
            bit = 0
            while string:
                container |= string.pop(0)<<bit
                bit += 15
                while bit >= 9:
                    bit -= 9
                    c = container&0x1FF
                    if c == 0x1FF:
                        newstring.append(0xFFFF)
                    else:
                        newstring.append(c)
                    container >>= 9
            string = newstring
        text = ""
        while string:
            char = string.pop(0)
            if char == 0xFFFF:
                break
            elif char == 0xFFFE:
                try:
                    kind = string.pop(0)
                    count = string.pop(0)
                    text += "VAR("
                    args = [kind]
                    for k in range(count):
                        args.append(string.pop(0))
                except IndexError:
                    break
                text += ", ".join(map(str, args))
                text += ")"
            elif char == 0xE000:
                text += "\\n"
            elif char == 0x25BC:
                text += "\\r"
            elif char == 0x25BD:
                text += "\\f"
            else:
                try:
                    text += unicodeparser.tb[char]
                except:
                    text += "\\x%04X"%char
        e = "0_%i"%i
        if compressed:
            e += "c" # 0_2c = ....
        texts.append([e, text])
    if hasComments:
        reader.seek(commentOfs)
        num = reader.read16()
        for i in range(num):
            commentid = reader.read16()
            text = ""
            c = 0
            while True:
                c = reader.read16()
                if c == 0xFFFF:
                    break
                text += unichr(c)
            e = "Comment_%i"%commentid
            texts.append([e, text])
    return sorted(texts, cmp=sortTextKeys)
    
def gen4put(texts):
    stringwriter = binarywriter()
    ofs = {}
    sizes = {}
    comments = {}
    for entry in texts:
        match = re.match("([^_]+)_([0-9]+)(.*)", entry[0])
        if not match:
            continue
        blockid = match.group(1)
        textid = int(match.group(2))
        flags = match.group(3)
        text = entry[1]
        if blockid.lower() == "comment":
            comments[textid] = text
            continue
        ofs[textid] = stringwriter.pos()
        key = (0x91BD3*(textid+1))&0xFFFF # still not sure about that 9
        dec = []
        while text:
            c = text[0]
            text = text[1:]
            if c == '\\':
                c = text[0]
                text = text[1:]
                if c == 'x':
                    n = int(text[:4], 16)
                    text = text[4:]
                elif c == 'n':
                    n = 0xe000
                elif c == 'r':
                    n = 0x25BC
                elif c == 'f':
                    n = 0x25BD
                else:
                    n = 1
                dec.append(n)
            elif c == 'V':
                if text[:2] == "AR":
                    text = text[3:] # also skip (
                    eov = text.find(")")
                    args = map(int, text[:eov].split(","))
                    text = text[eov+1:]
                    dec.append(0xFFFE)
                    dec.append(args.pop(0))
                    dec.append(len(args))
                    for a in args:
                        dec.append(a)
                else:
                    dec.append(unicodeparser.d['V'])
            else:
                dec.append(unicodeparser.d[c])
        size = len(dec)+1
        if "c" in flags:
            comp = [0xF100]
            container = 0
            bit = 0
            while dec:
                c = dec.pop(0)
                if c>>9:
                    print("Illegal compressed character: %i"%c)
                container |= c<<bit
                bit += 9
                while bit >= 15:
                    bit -= 15
                    comp.append(container&0xFFFF)
                    container >>= 15
            container |= 0xFFFF<<bit
            comp.append(container&0xFFFF)
            dec = comp[:]
        else:
            dec.append(0xFFFF)
        for d in dec:
            stringwriter.write16(d^key)
            key = (key+0x493D)&0xFFFF
        sizes[textid] = size
    seed = 255
    num = max(ofs)+1
    ref = min(ofs)
    for i in range(num):
        if i not in ofs:
            ofs[i] = 0
            sizes[i] = 0
    if comments:
        aofs = 12+num*8
        seed |= 0x100
    else:
        aofs = 4+num*8
    writer = binarywriter()
    writer.write16(num)
    writer.write16(seed)
    for i in range(num):
        tmp = ((((seed*0x2FD)&0xFFFF)*(i+1))&0xFFFF)
        key = tmp | (tmp << 16)
        writer.write32((aofs+ofs[i])^key)
        writer.write32(sizes[i]^key)
    if comments:
        tmp = ((((seed*0x2FD)&0xFFFF)*(i+1))&0xFFFF)
        key = tmp | (tmp << 16)
        writer.write32((aofs+stringwriter.pos())^key)
        writer.write32(0xFFFF^key)
    writer.writear(stringwriter.toarray())
    if comments:
        writer.write16(len(comments))
        for commentid in comments:
            writer.write16(commentid)
            for c in unicode(comments[commentid]):
                writer.write16(ord(c))
            writer.write16(0xFFFF)
    return writer.tostring()
    
def gen5get(f):
    texts = []
    reader = binaryreader(f)
    
    numblocks = reader.read16()
    numentries = reader.read16()
    filesize = reader.read32()
    zero = reader.read32()
    blockoffsets = []
    for i in range(numblocks):
        blockoffsets.append(reader.read32())
    # filesize == len(f)-reader.pos()
    for i in range(numblocks):
        reader.seek(blockoffsets[i])
        size = reader.read32()
        tableoffsets = []
        charcounts = []
        textflags = []
        for j in range(numentries):
            tableoffsets.append(reader.read32())
            charcounts.append(reader.read16())
            textflags.append(reader.read16())
        for j in range(numentries):
            compressed = False
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
                decchars.insert(0, char)
            if decchars[0] == 0xF100:
                compressed = True
                decchars.pop(0)
                newstring = []
                container = 0
                bit = 0
                while decchars:
                    container |= decchars.pop(0)<<bit
                    bit += 16
                    while bit >= 9:
                        bit -= 9
                        c = container&0x1FF
                        if c == 0x1FF:
                            newstring.append(0xFFFF)
                        else:
                            newstring.append(c)
                        container >>= 9
                decchars = newstring
            while decchars:
                c = decchars.pop(0)
                if c == 0xFFFF:
                    break
                elif c == 0xFFFE:
                    text += "\\n"
                elif c < 20 or c > 0xF000:
                    text += "\\x%04X"%c
                elif c == 0xF000:
                    try:
                        kind = decchars.pop(0)
                        count = decchars.pop(0)
                        if kind == 0xbe00 and count == 0:
                            text += "\\f"
                            continue
                        if kind == 0xbe01 and count == 0:
                            text += "\\r"
                            continue
                        text += "VAR("
                        args = [kind]
                        for k in range(count):
                            args.append(decchars.pop(0))
                    except IndexError:
                        break
                    text += ", ".join(map(str, args))
                    text += ")"
                else:
                    text += unichr(c)
            e = "%i_%i"%(i, j)
            flag = ""
            val = textflags[j]
            c = 65
            while val:
                if val&1:
                    flag += chr(c)
                c += 1
                val >>= 1
            if compressed:
                flag += "c"
            e += flag
            texts.append([e, text])
    return texts
    
def gen5put(texts):
    textofs = {}
    sizes = {}
    comments = {}
    textflags = {}
    blockwriters = {}
    for entry in texts:
        match = re.match("([^_]+)_([0-9]+)(.*)", entry[0])
        if not match:
            continue
        blockid = match.group(1)
        textid = int(match.group(2))
        flags = match.group(3)
        text = entry[1]
        if blockid.lower() == "comment":
            comments[textid] = text
            continue
        blockid = int(blockid)
        if blockid not in blockwriters:
            blockwriters[blockid] = binarywriter()
            textofs[blockid] = {}
            sizes[blockid] = {}
            textflags[blockid] = {}
        textofs[blockid][textid] = blockwriters[blockid].pos()
        dec = []
        while text:
            c = text[0]
            text = text[1:]
            if c == '\\':
                c = text[0]
                text = text[1:]
                if c == 'x':
                    n = int(text[:4], 16)
                    text = text[4:]
                elif c == 'n':
                    n = 0xFFFE
                elif c == 'r':
                    dec.append(0xF000)
                    dec.append(0xbe01)
                    dec.append(0)
                    continue
                elif c == 'f':
                    dec.append(0xF000)
                    dec.append(0xbe00)
                    dec.append(0)
                    continue
                else:
                    n = 1
                dec.append(n)
            elif c == 'V':
                if text[:2] == "AR":
                    text = text[3:]
                    eov = text.find(")")
                    args = map(int, text[:eov].split(","))
                    text = text[eov+1:]
                    dec.append(0xF000)
                    dec.append(args.pop(0))
                    dec.append(len(args))
                    for a in args:
                        dec.append(a)
                else:
                    dec.append(ord('V'))
            else:
                dec.append(ord(c))
        flag = 0
        for i in range(16):
            if chr(65+i) in flags:
                flag |= 1<<i
        textflags[blockid][textid] = flag
        if "c" in flags:
            comp = [0xF100]
            container = 0
            bit = 0
            while dec:
                c = dec.pop(0)
                if c>>9:
                    print("Illegal compressed character: %i"%c)
                container |= c<<bit
                bit += 9
                while bit >= 16:
                    bit -= 16
                    comp.append(container&0xFFFF)
                    container >>= 16
            container |= 0xFFFF<<bit
            comp.append(container&0xFFFF)
            dec = comp[:]
        key = 0
        enc = []
        while dec:
            char = dec.pop() ^ key
            key = ((key>>3)|(key<<13))&0xFFFF
            enc.insert(0, char)
        enc.append(key^0xFFFF)
        sizes[blockid][textid] = len(enc)
        for e in enc:
            blockwriters[blockid].write16(e)
    numblocks = max(blockwriters)+1
    if numblocks != len(blockwriters):
        raise KeyError
    numentries = 0
    for block in blockwriters:
        numentries = max(numentries, max(textofs[block])+1)
    offsets = []
    baseofs = 12+4*numblocks
    textblock = binarywriter()
    for i in range(numblocks):
        data = blockwriters[i].toarray()
        offsets.append(baseofs+textblock.pos())
        relofs = numentries*8+4
        textblock.write32(len(data)+relofs)
        for j in range(numentries):
            textblock.write32(textofs[i][j]+relofs)
            textblock.write16(sizes[i][j])
            textblock.write16(textflags[i][j])
        textblock.writear(data)
    writer = binarywriter()
    writer.write16(numblocks)
    writer.write16(numentries)
    writer.write32(textblock.pos())
    writer.write32(0)
    for i in range(numblocks):
        writer.write32(offsets[i])
    writer.writear(textblock.toarray())
    return writer.tostring()
    
def get(gen, f):
    if gen == 5:
        return gen5get(f)
    return gen4get(f)
    
def put(gen, texts):
    if gen == 5:
        return gen5put(texts)
    return gen4put(texts)