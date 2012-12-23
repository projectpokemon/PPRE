from compat import configparser

#config version
version = 1

"""options = {
    "configversion":{"default":version, "required":True, "description":"Config version"},
    "file":{"required":False, "description":"ROM location"},
    "directory":{"required":True, "description":"Project Directory"},
    "projectname":{"default":"No name", "required":True, "description":"Project Name"},
    "projectdescription":{"default":"No description", "description":"Project Description"},
    "projectversion":{"default": "0", "description":"Project Version"},
    "projectrom":{"description":"Default Output ROM Location"}
}"""

sections = ["location", "project"]
options = {
    "location": ["base", "directory"],
    "project": ["name", "description", "version", "output"],
}

def qtSetter(s, o, v, meta):
    meta[s+"_"+o+"_value"].setText(v)
    
def qtGetter(s, o, meta):
    return str(meta[s+"_"+o+"_value"].text())

def load(f, setter, meta=None):
    parser = configparser.ConfigParser()
    parser.readfp(f)
    for s in sections:
        for o in options[s]:
            setter(s, o, parser.get(s, o), meta)
    
def write(f, getter, meta=None):
    parser = configparser.ConfigParser()
    parser.add_section("config")
    parser.set("config", "version", str(version))
    for s in sections:
        parser.add_section(s)
        for o in options[s]:
            parser.set(s, o, getter(s, o, meta))
    parser.write(f)
    
project = None
mw = None
    
if __name__ == "__main__":
    with open("sample.pprj", "w") as f:
        write(f, lambda x, y:"")