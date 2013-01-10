import array

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
        
class binarywriter:
    def __init__(self):
        self.s = array.array('H')
    def write16(self, i):
        self.s.append(i)
    def write32(self, i):
        self.s.append(i&0xFFFF)
        self.s.append((i>>16)&0xFFFF)
    def writear(self, a):
        self.s.extend(a)
    def tostring(self):
        return self.s.tostring()
    def toarray(self):
        return self.s
    def pos(self):
        return len(self.s)<<1
