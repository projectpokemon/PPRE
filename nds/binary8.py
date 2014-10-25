import array

class binaryreader:
    def __init__(self, string):
        self.s = array.array('B',string)
        self.ofs = 0
        self.ReadUInt8 = self.read8
        self.ReadUInt16 = self.read16
        self.ReadUInt32 = self.read32
        self.Seek = self.seek
    def read8(self):
        ret = self.s[self.ofs]
        self.ofs += 1
        return ret
    def read16(self):
        ret = self.s[self.ofs] | (self.s[self.ofs+1]<<8)
        self.ofs += 2
        return ret
    def read32(self):
        ret = self.s[self.ofs] | (self.s[self.ofs+1]<<8)
        ret |= (self.s[self.ofs+2]<<16) | (self.s[self.ofs+3]<<24)
        self.ofs += 4
        return ret
    def seek(self, ofs):
        self.ofs = ofs
    def pos(self):
        return self.ofs
        
class binarywriter:
    def __init__(self):
        self.s = array.array('B')
    def write8(self, i):
        self.s.append(i)
    def write16(self, i):
        self.s.append(i&0xFF)
        self.s.append((i>>8)&0xFF)
    def write32(self, i):
        self.s.append(i&0xFF)
        self.s.append((i>>8)&0xFF)
        self.s.append((i>>16)&0xFF)
        self.s.append((i>>24)&0xFF)
    def writear(self, a):
        self.s.extend(a)
    def tostring(self):
        return self.s.tostring()
    def toarray(self):
        return self.s
    def pos(self):
        return len(self.s) 
