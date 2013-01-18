import config

gameids = {"ADA":"Diamond", "CPU":"Platinum", "IPK":"HeartGold", 
    "IPG":"SoulSilver", "IRB":"Black", "IRA":"White", "IRE":"Black2",
    "IRD":"White2"}
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
        realgame = gameids[game]
    else:
        realgame = "Unknown"
    for p in pairs:
        if realgame in p:
            gamename = p[0]
            break
    return (gamename, lang, romversion, realgame)
    
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
        "Evolution":"/poketool/personal/evo.narc",
        "Moves":"/poketool/personal/wotbl.narc"},
    "HeartGold":{
        "Personal":"/a/0/0/2",
        "Evolution":"/a/0/3/4"},
    "SoulSilver":{
        "Personal":"/a/0/0/2",
        "Evolution":"/a/0/3/4"},
    "Black":{
        "Personal":"/a/0/1/6",
        "Evolution":"/a/0/1/9"},
    "White":{
        "Personal":"/a/0/1/6",
        "Evolution":"/a/0/1/9"},
    "Black2":{
        "Personal":"/a/0/1/6",
        "Evolution":"/a/0/1/9"},
    "White2":{
        "Personal":"/a/0/1/6",
        "Evolution":"/a/0/1/9"},
}

movefiles = {
    "Diamond":{"Moves":"/poketool/waza/waza_tbl.narc"},
    "Pearl":{"Moves":"/poketool/waza/waza_tbl.narc"},
    "Platinum":{"Moves":"/poketool/waza/pl_waza_tbl.narc"},
    "HeartGold":{"Moves":"/a/0/1/1"},
    "SoulSilver":{"Moves":"/a/0/1/1"},
    "Black":{"Moves":"/a/0/2/1"},
    "White":{"Moves":"/a/0/2/1"},
    "Black2":{"Moves":"/a/0/2/1"},
    "White2":{"Moves":"/a/0/2/1"},
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
            "PokemonNames":{
                "English":362
            },
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
    "Pearl":{
        "English":{
            "Locations":382,
            "Types":565,
            "Abilities":552,
            "Items":344,
            "Moves":588,
            "Pokemon":362,
            "PokemonNames":{
                "English":362
            },
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
    "Platinum":{
        "English":{
            "Locations":433,
            "Types":624,
            "Abilities":611,
            "Items":392,
            "ItemRefs":{
                "Names":392,
                "Var":393,
                "Plural":394
            },
            "Moves":648,
            "Pokemon":412,
            "PokemonNames":{
                "English":412
            },
            "Weight":708,
            "Height":709,
            "Species":711, # or 718?
            "Flavor":{
                "Diamond":698,
                "Pearl":699,
                "Platinum":706,
            },
            "Class":619,
            "Trainers":618,
            "Trainer Quotes":613,
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
            "PokemonNames":{
                "English": 237
            },
        },
    },
    "SoulSilver":{
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
            "PokemonNames":{
                "English": 237
            },
        },
    },
    "Black":{
        "English":{
            "Pokemon": 70,
            "Types": 199,
            "Abilities": 182,
            "Moves": 203,
            "Items": 54,
            "Species": 260,
            "Flavor":{
                "Black": 235,
                "White": 236
            },
            "PokemonNames":{
                "English": 70
            },
            
        },
    },
    "White":{
        "English":{
            "Pokemon": 70,
            "Types": 199,
            "Abilities": 182,
            "Moves": 203,
            "Items": 54,
            "Species": 260,
            "Flavor":{
                "Black": 235,
                "White": 236
            },
            "PokemonNames":{
                "English": 70
            },
            
        },
    },
    "Black2":{
        "English":{
            "Pokemon": 90,
            "Types": 489,
            "Abilities": 374,
            "Moves": 403,
            "Items": 64,
            "Species": 464,
            "Flavor":{
                "2": 442,
            },
            "PokemonNames":{
                "English": 90
            },
            
        },
    },
}