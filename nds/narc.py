from struct import *
from array import *

class BTAF:
    def __init__(self, rawdata):
        if len(rawdata)>0:           
            self.magic = rawdata[:4]
            self.header = unpack("II", rawdata[4:12])
            if self.magic != "BTAF":
                raise NameError, "BTAF tag not found"
        else:
            self.magic = "BTAF"
            self.header = (12, 0)
        self.table = []
        rawdata=rawdata[12:]
        if len(rawdata)>0:
            for i in range(self.getEntryNum()):            
                self.table.append(unpack("II", rawdata[i*8:i*8+8]))      
    def getSize(self):
        return self.header[0]
    def getEntryNum(self):
        return self.header[1]
    def toString(self, gmif):
        ret = "BTAF"+pack("II", self.header[0], self.header[1])
        for ofs, l in gmif.getEntries():
            ret += pack("II", ofs, ofs+l)
        return ret

class BTNF:
    def __init__(self, rawdata):
        if len(rawdata)>0:
            self.magic = rawdata[:4]
            self.header = unpack("IIHH", rawdata[4:0x10])
            if self.magic != "BTNF":
                raise NameError, "BTNF tag not found"
        else:
            self.magic = "BTNF"
            self.header = (16, 4, 0, 1)
    def toString(self):
        ret = "BTNF"
        ret += pack("IIHH", self.header[0], self.header[1], self.header[2],
            self.header[3])
        return ret
class GMIF:
    def __init__(self, rawdata, t):
        if len(rawdata)>0:
            self.magic = rawdata[:4]
            self.size = unpack("I", rawdata[4:8])[0]
            if self.magic != "GMIF":
                raise NameError, "GMIF tag not found"         
        else:
            self.magic = "GMIF"
            self.size = 8
        self.files = []
        for ofs in t:
            self.files.append(rawdata[8+ofs[0]:8+ofs[1]])
    def getEntries(self):
        ret = []
        of = 0
        for f in self.files:
            l = len(f)
            ret.append([of, l])
            while l%4:
                l += 1
            of += l
        return ret
    def toString(self):
        ret = ""
        for f in self.files:
            ret += f
            l = len(f)
            while l%4:
                l += 1
                ret += "\x00"
        self.size = len(ret)
        return "GMIF"+pack("I", self.size)+ret
class NARC:
    def __init__(self, rawdata):
        if len(rawdata)>0:
            self.magic = rawdata[:4]
            if self.magic != "NARC":
                raise NameError, "NARC tag not found"
            self.header = unpack("IIHH", rawdata[4:16])
        else:
            self.magic = "NARC"
            self.header = (0x0100FFFE, 0x10+12+8 + 0x10, 0x10, 3)
        rawdata= rawdata[16:]
        self.btaf = BTAF(rawdata)
        rawdata= rawdata[self.btaf.getSize():]
        self.btnf = BTNF(rawdata)
        rawdata= rawdata[self.btnf.header[0]:]
        self.gmif = GMIF(rawdata, self.btaf.table)
    def toString(self):
        ret = "NARC"
        ret += pack("IIHH", self.header[0], self.header[1], self.header[2],
            self.header[3]) + self.btaf.toString(self.gmif)
        ret += self.btnf.toString()+self.gmif.toString()
        return ret
    def toFile(self, f):
        f.write(self.toString())

    def __getitem__(self, key):
        return self.gmif.files[key]

    def __len__(self):
        return len(self.gmif.files)
