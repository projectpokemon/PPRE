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
    def ToFile(self, f, t):
        f.write(self.magic)
        f.write(pack("II", self.header[0],self.header[1]))
        
        for pair in t:            
            f.write(pack("II", pair[0], pair[1]))
    def addFile(self):
        s, e=self.header
        s += 8
        e += 1
        self.header=s, e
        
               
    
 
    
    
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
    def ToFile(self, f):
        f.write(self.magic)
        f.write(pack("IIHH", self.header[0],self.header[1],self.header[2],self.header[3]))
        
    
            
        

 
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
            
    def appendFile(raw):
        data += raw
        self.header.size += len(raw)
    def ToFile(self, f):
        f.write(self.magic)
        f.write(pack("I", self.size))
        for d in self.files:
            f.write(d)            
    def addFile(self, data, size):
        self.files.append(data)
        self.size += size        
    def buildIndex(self):
        index = []
        c = 0
        for f in self.files:
            l = len(f)
            index.append((c, c+l))
            c=c+l
        return index
    

        
    
        

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

    def ToFile(self, f):
        f.write(self.magic)
        f.write(pack("IIHH", self.header[0],self.header[1],self.header[2],self.header[3]))
        self.btaf.ToFile(f, self.gmif.buildIndex())
        self.btnf.ToFile(f)
        self.gmif.ToFile(f)
    def addFile(self, s):
        size = len(s)
        mark, narcsz, hdrsize, sect = self.header
        narcsz += (size + 8)
        self.header = (mark, narcsz, hdrsize, sect)
        self.btaf.addFile()
        self.gmif.addFile(s, size)
    def replaceFile(self, index, s):
        newmold = len(s) - len(self.gmif.files[index])
        mark, narcsz, hdrsize, sect = self.header
        narcsz += (newmold)
        self.header = (mark, narcsz, hdrsize, sect)
        self.gmif.size += (newmold)
        self.gmif.files[index] = s
