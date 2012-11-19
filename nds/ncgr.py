from struct import *
from PIL import Image, ImagePalette

class CHAR:
    def __init__(self, rawdata, attribs): 
        self.magic = rawdata[:4]
        if self.magic != "RAHC":
            raise NameError, "RAHC tag not found"
        self.header = [-1]
        self.header[0], self.width, self.height, self.depth = unpack("IHHI", rawdata[4:16])
        u0, nottiled, parted, u1, self.scrsize, self.scrdataofs = unpack("IBBHII", rawdata[16:32])
        self.tiled = not nottiled
        if parted or u0:
            self.width = 8
            self.height = self.scrsize>>6
        decrypt = lambda x: x
        for attr in attribs:
            if attr == "width":
                self.width = attribs[attr]
            elif attr == "height":
                self.height = attribs[attr]
            elif attr == "decrypt":
                decrypt = attribs[attr]
        rawdata = decrypt(rawdata[32:])
        self.tiles = []
        if self.tiled:
            for l in range(self.height):
                row = []
                for m in range(self.width):
                    col = []
                    for n in range(8):
                        tilerow = []
                        for p in range(4):
                            if self.depth == 0x3:
                                try:
                                    tmp = unpack("B", rawdata[:1])[0]
                                    rawdata = rawdata[1:]
                                except:
                                    tmp = 0
                                tilerow.append(tmp&0xf)
                                tilerow.append(tmp>>4)
                            else:
                                tmp1, tmp2 = unpack("BB", rawdata[:2])
                                rawdata = rawdata[2:]
                                tilerow.append(tmp1)
                                tilerow.append(tmp2)
                        col.append(tilerow)
                    row.append(col)
                self.tiles.append(row)
        else:
            for l in range(self.height*8):
                row = []
                for m in range(self.width*4):
                    if self.depth == 0x3:
                        tmp = unpack("B", rawdata[:1])[0]
                        rawdata = rawdata[1:]
                        row.append(tmp&0xf)
                        row.append(tmp>>4)
                    else:
                        tmp1, tmp2 = unpack("BB", rawdata[:2])
                        rawdata = rawdata[2:]
                        row.append(tmp1)
                        row.append(tmp2)
                self.tiles.append(row)
    def toString(self):
        data = ""
        lenL = len(self.tiles)
        for l in range(lenL):
            lenM = len(self.tiles[l])
            if self.tiled:
                for n in range(8):
                    for m in range(lenM):
                        for p in range(8):
                            data += chr(self.tiles[l][m][n][p])
            else:
                for m in range(lenM):
                    data += chr(self.tiles[l][m])
        return data

class NCGR:
    def __init__(self, rawdata, attribs={}):
        """
        attribs["height"] = CHAR height,
        attribs["widght"] = CHAR width
        attribs["decrypt"] = decryption algorithm: rawdata[decofs:] = dec(rawdata[decofs:])
        """
        self.magic = rawdata[:4]
        if self.magic != "RGCN":
            raise NameError, "RGCN tag not found"
        self.header = unpack("III", rawdata[4:16])
        rawdata = rawdata[16:]
        self.char = CHAR(rawdata, attribs)
    def toImage(self):
        palette = ImagePalette.ImagePalette("RGB")
        palette.dirty = 1
        for i in range(256):
            k = (i*48)%256
            palette.palette[i] = [k, k, k]
        w = self.char.width*8
        h = self.char.height*8
        data = self.char.toString()
        if not w or not h:
            return Image.fromstring("P", (1, 1), "\x00")
        return Image.fromstring("P", (w, h), data)