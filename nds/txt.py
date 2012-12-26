import narc
import struct
import cStringIO as StringIO
import unicodeparser
from binary16 import binaryreader, binarywriter
        
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
            e = "[c]"+e
        texts.append([e, text])
    return texts
    
def gen4put(texts):
    writer = binarywriter()
    num = len(texts)
    stringwriter = binarywriter()
    ofs = []
    sizes = []
    for i, entry in enumerate(texts):
        #TODO: entry[0]
        text = entry[1]
        ofs.append(stringwriter.pos())
        size = 0
        key = (0x91BD3*(i+1))&0xFFFF
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
        dec.append(0xFFFF)
        for d in dec:
            stringwriter.write16(d^key)
            key = (key+0x493D)&0xFFFF
            size += 1
        sizes.append(size)
    seed = 0x7EA # No idea if this has to be anything special
    aofs = 4+num*8
    writer.write16(num)
    writer.write16(seed)
    for i in range(num):
        tmp = ((((seed*0x2FD)&0xFFFF)*(i+1))&0xFFFF)
        key = tmp | (tmp << 16)
        writer.write32((aofs+ofs[i])^key)
        writer.write32(sizes[i]^key)
    writer.writear(stringwriter.toarray())
    return writer.tostring()
    
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