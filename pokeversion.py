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
    
textfiles = {
    "Diamond":{"Main":"/msgdata/msg.narc"},
    "Pearl":{"Main":"/msgdata/msg.narc"},
    "Platinum":{"Main":"/msgdata/pl_msg.narc"},
    "HeartGold":{"Main":"/a/0/2/7"},
    "SoulSilver":{"Main":"/a/0/2/7"},
    "Black":{"Main":"/a/0/0/2", "Story":"/a/0/0/3"},
    "White":{"Main":"/a/0/0/2", "Story":"/a/0/0/3"},
    "Black2":{"Main":"/a/0/0/2", "Story":"/a/0/0/3"},
    "White2":{"Main":"/a/0/0/2", "Story":"/a/0/0/3"},
}

pokemonfiles = {
    "Diamond":{
        "Personal":"/poketool/personal/personal.narc",
        "Evolution":"/poketool/personal/evo.narc"},
    "HeartGold":{
        "Personal":"/a/0/0/2",
        "Evolution":"/a/0/3/4"},
}
    
textentries = {
    "Diamond":{
        "English":{
            "Locations":382,
            "Types":565,
            "Abilities":552,
            "Items":344,
            "Moves":588,
            "Pokemon":362,
            "Weight":619,
            "Height":620,
            "Species":621,
            "Flavor":{
                "Diamond":615,
                "Pearl":616
            },
            "Class":560,
            "Trainers":559,
            "Trainer Quotes":555,
        },
    },
    "HeartGold":{
        "English":{
            "Locations": 279, 
            "Types": 735, 
            "Abilities": 720, 
            "Items": 222, 
            "Moves": 750, 
            "Pokemon": 237,
            "Height": 814,
            "Weight": 812,
            "Flavor":{
                "HeartGold": 803,
                "SoulSilver": 804,
            },
            "Species": 823,
            "Class": 730,
            "Trainers": 729,
        },
    },
}