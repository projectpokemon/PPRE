import codecs
tb = {}
d = {}
f = codecs.open("Table.tbl",encoding="utf-16")
l = f.readlines()
for q in l:
    r=q.split("=", 1)
    r[1]=r[1].rstrip("\r\n")
    tb[int(r[0], 16)]=r[1]
    d[r[1]] = int(r[0], 16)
    
#print tb[3]
