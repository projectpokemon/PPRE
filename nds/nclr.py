from struct import *

class PLTT:
    def __init__(self, rawdata): 
        self.magic = rawdata[:4]
        if self.magic != "TTLP":
            raise NameError, "TTLP tag not found"
        self.header = unpack("IIIII", rawdata[4:24])
        rawdata = rawdata[24:]
        self.colors = []
        for i in range(self.getEntryNum()):
            try:
                tmp = unpack("H", rawdata[:2])[0]
            except:
                print("Failed", i, self.getEntryNum(), self.header)
                exit()
            rawdata = rawdata[2:]
            self.colors.append(((tmp&0x1f)<<3,((tmp>>5)&0x1f)<<3,((tmp>>10)&0x1f)<<3))
            
        
    def getSize(self):
        return self.header[0]
    def getEntryNum(self):
        return self.header[4]

class NCLR:
    def __init__(self, rawdata): 
        self.magic = rawdata[:4]
        if self.magic != "RLCN":
            raise NameError, "RLCN tag not found"
        self.header = unpack("III", rawdata[4:16])
        rawdata = rawdata[16:]
        self.pltt = PLTT(rawdata)