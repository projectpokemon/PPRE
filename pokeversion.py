import config

gameids = {"ADA":"Diamond", "CPU":"Platinum", "IPK":"HeartGold", 
    "IPG":"SoulSilver", "IRB":"Black", "IRA":"White", "IRE":"Black2"}
langs = {"E":"English", "J":"Japanese", "O":"English", "K":"Korean"}
pairs = [["Diamond", "Pearl"], ["Platinum"], ["HeartGold", "SoulSilver"],
    ["Black", "White"], ["Black2", "White2"]]
gens = {"Diamond":4, "Pearl":4, "Platinum":4, "HeartGold":4, "SoulSilver":4,
    "Black":5, "White":5, "Black2":5, "White2":5}

def get():
    if not config.project:
        return (None, None, None)
    header = open(config.project["directory"]+"/header.bin", "rb")
    header.seek(0xC)
    code = header.read(4)
    romversion = int(header.read(2))
    game = code[:3]
    lang = code[3]
    if game in gameids:
        gamename = gameids[game]
    else:
        gamename = "Unknown"
        
    return (gamename, lang, romversion)