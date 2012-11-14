import os

def defaultopen(f, title):
    f.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>%s</title>
</head>
<body>
"""%title)

def defaultclose(f, title):
    f.write("""
</body>
</html>
""")

def defaultmkdir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def defaultidxopen(f, title):
    return

try:
    from customtemplate import *
except:
    pass

class templatefile(file):
    def __init__(self, name, mode="w", title="Data"):
        super(templatefile, self).__init__(name, mode)
        self.title = title
        defaultopen(self, self.title)
    def close(self):
        defaultclose(self, self.title)
        super(templatefile, self).close()
        
class idxfile(templatefile):
    def __init__(self, name, mode="w", title="Data"):
        super(templatefile, self).__init__(name, mode)
        self.title = title
        defaultopen(self, self.title)
        defaultidxopen(self, self.title)
    def close(self):
        defaultclose(self, self.title)
        super(templatefile, self).close()
mkdir = defaultmkdir
open = templatefile