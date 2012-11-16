#!/usr/bin/env python
import os, sys
import struct
import template

allowed_games = ["diamond", "platinum", "heartgold", "black", "black2"]
EXT = "php"
genindex = False
games = []

args = sys.argv[1:]
while args:
    a = args.pop(0)
    if a == "--help":
        print("""Usage: %s [Options] [Game1 [Game2 [...]]]
If game is left blank, all games will be processed.

Options:
--gen-index         Generate index files.
--ext <extension>   Use <extension> for newly created files.
--help              Show this help, then exit.

Valid Games:
%s
"""%(sys.argv[0], ", ".join(allowed_games)))
        exit()
    if a == "--gen-index":
        genindex = True
        continue
    if a == "--ext":
        EXT = args.pop(0)
        continue
    if a in allowed_games:
        games.append(a)
if not games:
    games = allowed_games
FEXT = "."+EXT

struct_name = {"B": "UInt8", "H":"UInt16", "I":"UInt32"}


fs = {
    "diamond":{
        "/poketool/personal/personal.narc":"<a href='pokedex"+FEXT+"'>Pokemon data</a>",
        "/poketool/personal/growtbl.narc":"<a href='exprate"+FEXT+"'>Experience Table</a>",
        "/poketool/personal/evo.narc":"<a href='evo"+FEXT+"'>Evolutions</a>",
        "/poketool/personal/wotbl.narc":"<a href='levelmoves"+FEXT+"'>Level-Up Moves</a>",
        "/poketool/personal/pms.narc":"<a href='baseevo"+FEXT+"'>Base Evolutions/Baby Pokemon</a>",
        "/poketool/trainer/trdata.narc":"<a href='trdata"+FEXT+"'>Trainer data</a>",
        "/fielddata/encountdata/d_enc_data.narc":"<a href='enc"+FEXT+"'>Encounter Data</a>",
        "/fielddata/encountdata/p_enc_data.narc":"Pearl Encounter Data",
        "/msgdata/msg.narc":"<a href='msg"+FEXT+"'>Text/Message Files</a>",
        "/application/zukanlist/zukan_data/zukan_data.narc":"<a href='search"+FEXT+"'>Dex Search Files</a>",
        },
    "platinum":{
        "/poketool/personal/pl_personal.narc":"<a href='pokedex"+FEXT+"'>Pokemon data</a>",
        "/poketool/personal/pl_growtbl.narc":"<a href='exprate"+FEXT+"'>Experience Table</a>",
        "/poketool/personal/evo.narc":"<a href='evo"+FEXT+"'>Evolutions</a>",
        "/poketool/personal/wotbl.narc":"<a href='levelmoves"+FEXT+"'>Level-Up Moves</a>",
        "/poketool/personal/pms.narc":"<a href='baseevo"+FEXT+"'>Base Evolutions/Baby Pokemon</a>",
        "/poketool/trainer/trdata.narc":"<a href='trdata"+FEXT+"'>Trainer data</a>",
        "/fielddata/encountdata/pl_enc_data.narc":"<a href='enc"+FEXT+"'>Encounter Data</a>",
        "/msgdata/pl_msg.narc":"<a href='msg"+FEXT+"'>Text/Message Files</a>",
        "/application/zukanlist/zukan_data/zukan_data_gira.narc":"<a href='search"+FEXT+"'>Dex Search Files</a>",
        
        "/poketool/personal/personal.narc":"DP Pokemon Data",
        "/poketool/personal/growtbl.narc":"DP Experience Table",
        "/fielddata/encountdata/d_enc_data.narc":"Diamond Encounter Data",
        "/fielddata/encountdata/p_enc_data.narc":"Pearl Encounter Data",
        "/msgdata/msg.narc":"DP Message Files",
        "/application/zukanlist/zukan_data/zukan_data.narc":"DP Dex Search Files",
        },
    "heartgold":{
        "/a/0/0/2":"<a href='pokedex"+FEXT+"'>Pokemon data</a>",
        "/a/0/0/3":"<a href='exprate"+FEXT+"'>Experience Table</a>",
        "/a/0/3/4":"<a href='evo"+FEXT+"'>Evolutions</a>",
        "/a/0/3/3":"<a href='levelmoves"+FEXT+"'>Level-Up Moves</a>",
        "/poketool/personal/pms.narc":"<a href='baseevo"+FEXT+"'>Base Evolutions/Baby Pokemon</a>",
        "/a/0/5/5":"<a href='trdata"+FEXT+"'>Trainer data</a>",
        "/a/0/3/7":"<a href='enc"+FEXT+"'>Encounter Data</a>",
        "/a/0/2/7":"<a href='msg"+FEXT+"'>Text/Message Files</a>",
        "/a/0/7/4":"<a href='search"+FEXT+"'>Dex Search Files</a>",
        },
    "black":{
        "/a/0/0/2":"<a href='msg"+FEXT+"'>Text/Message Files</a>",
        "/a/0/0/3":"<a href='msg2"+FEXT+"'>Text/Story Files</a>",
        "/a/0/1/6":"<a href='pokedex"+FEXT+"'>Pokemon data</a>",
        "/a/0/1/7":"<a href='exprate"+FEXT+"'>Experience Table</a>",
        "/a/0/1/8":"<a href='levelmoves"+FEXT+"'>Level-Up Moves</a>",
        "/a/0/1/9":"<a href='evo"+FEXT+"'>Evolutions</a>",
        "/a/0/2/0":"<a href='baseevo"+FEXT+"'>Base Evolutions/Baby Pokemon</a>",
        "/a/0/9/2":"<a href='trdata"+FEXT+"'>Trainer data</a>",
        "/a/1/2/6":"Encounter Data",
        },
    "black2":{
        "/a/0/0/2":"<a href='msg"+FEXT+"'>Text/Message Files</a>",
        "/a/0/0/3":"<a href='msg2"+FEXT+"'>Text/Story Files</a>",
        "/a/0/1/6":"<a href='pokedex"+FEXT+"'>Pokemon data</a>",
        "/a/0/1/7":"<a href='exprate"+FEXT+"'>Experience Table</a>",
        "/a/0/1/8":"<a href='levelmoves"+FEXT+"'>Level-Up Moves</a>",
        "/a/0/1/9":"<a href='evo"+FEXT+"'>Evolutions</a>",
        "/a/0/2/0":"<a href='baseevo"+FEXT+"'>Base Evolutions/Baby Pokemon</a>",
        "/a/0/9/2":"<a href='trdata"+FEXT+"'>Trainer data</a>",
        "/a/1/2/6":"Encounter Data",
        
        },
}

dexfmt = {}
dexfmt["diamond"] = ["BBBBBBBBBBHHHBBBBBBBBBB", 
    ["basehp"],
    ["baseatk"],
    ["basedef"],
    ["basespeed"],
    ["basespatk"],
    ["basespdef"],
    ["type1"],
    ["type2"],
    ["catchrate"],
    ["baseexp"],
    ["evs"],
    ["item1"],
    ["item2"],
    ["gender"],
    ["hatchcycle"],
    ["basehappy"],
    ["exprate"],
    ["egggroup1"],
    ["egggroup2"],
    ["ability1"],
    ["ability2"],
    ["flee"],
    ["color"]
]
dexfmt["platinum"] = dexfmt["diamond"][:]
dexfmt["heartgold"] = dexfmt["diamond"][:]
dexfmt["black"] = ["BBBBBBBBBBHHHHBBBBBBBBBBHHBBHHH", 
    ["basehp"],
    ["baseatk"],
    ["basedef"],
    ["basespeed"],
    ["basespatk"],
    ["basespdef"],
    ["type1"],
    ["type2"],
    ["catchrate"],
    ["stage"],
    ["evs"],
    ["item1"],
    ["item2"],
    ["item3"],
    ["gender"],
    ["hatchcycle"],
    ["basehappy"],
    ["exprate"],
    ["egggroup1"],
    ["egggroup2"],
    ["ability1"],
    ["ability2"],
    ["ability3"],
    ["flee"],
    ["formid"],
    ["form"],
    ["numforms"],
    ["color"],
    ["baseexp"],
    ["height"],
    ["weight"]
]
dexfmt["black2"] = dexfmt["black"][:]

evofmt = {}
evofmt["diamond"] = ["HHHHHHHHHHHHHHHHHHHHHxx",
    ["method1"],
    ["param1"],
    ["target1"],
    ["method2"],
    ["param2"],
    ["target2"],
    ["method3"],
    ["param3"],
    ["target3"],
    ["method4"],
    ["param4"],
    ["target4"],
    ["method5"],
    ["param5"],
    ["target5"],
    ["method6"],
    ["param6"],
    ["target6"],
    ["method7"],
    ["param7"],
    ["target7"],
]
evofmt["platinum"] = evofmt["diamond"][:]
evofmt["heartgold"] = evofmt["diamond"][:]
evofmt["black"] = evofmt["diamond"][:]
evofmt["black"][0] = "HHHHHHHHHHHHHHHHHHHHH"
evofmt["black2"] = evofmt["black"][:]

movefmt = {}
movefmt["diamond"] = ["H",
    ["moveid", 0, 8, 0x1FF],
    ["level", 9, 15, 0x7F],
]
movefmt["platinum"] = movefmt["diamond"][:]
movefmt["heartgold"] = movefmt["diamond"][:]
movefmt["black"] = ["I",
    ["moveid", 0, 15, 0xFFFF],
    ["level", 16, 31, 0xFFFF],
]
movefmt["black2"] = movefmt["black"][:]

trdatafmt = {}
trdatafmt["diamond"] = ["BBBBHHHHIBxxx",
    ["flag"],
    ["class"],
    ["battletype"],
    ["numpokemon"],
    ["item1"],
    ["item2"],
    ["item3"],
    ["item4"],
    ["ai"],
    ["battletype2"],
]
trdatafmt["platinum"] = trdatafmt["diamond"][:]
trdatafmt["heartgold"] = trdatafmt["diamond"][:] # TODO: may need fixing
trdatafmt["black"] = trdatafmt["diamond"][:] # TODO: may need fixing
trdatafmt["black2"] = trdatafmt["black"][:]

#file:///home/david/Dropbox/Public/py/ppre.pyw
# xxxxxxxxxxxxxxxxxxxxxxxx
encfmt = {}
encfmt["diamond"] = ["IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"+"IIIIII"+"IIIIIIIII"+
    "IBBxxIBBxxIBBxxIBBxxIBBxxI"+"x"*44+"IBBxxIBBxxIBBxxIBBxxIBBxxI"*3,
    "rate",
    "level1",
    "natid1",
    "level2",
    "natid2",
    "level3",
    "natid3",
    "level4",
    "natid4",
    "level5",
    "natid5",
    "level6",
    "natid6",
    "level7",
    "natid7",
    "level8",
    "natid8",
    "level9",
    "natid9",
    "level10",
    "natid10",
    "level11",
    "natid11",
    "level12",
    "natid12",
    "morning1",
    "morning2",
    "day1",
    "day2",
    "night1",
    "night2",
    "radar1",
    "radar2",
    "radar3",
    "radar4",
    "unknown1",
    "unknown2",
    "unknown3",
    "unknown4",
    "unknown5",
    "unknown6",
    "ruby1",
    "ruby2",
    "sapphire1",
    "sapphire2",
    "emerald1",
    "emerald2",
    "red1",
    "red2",
    "green1",
    "green2",
    "surfrate",
    "surf1maxlevel",
    "surf1minlevel",
    "surf1natid",
    "surf2maxlevel",
    "surf2minlevel",
    "surf2natid",
    "surf3maxlevel",
    "surf3minlevel",
    "surf3natid",
    "surf4maxlevel",
    "surf4minlevel",
    "surf4natid",
    "surf5maxlevel",
    "surf5minlevel",
    "surf5natid",
    "oldrodrate",
    "oldrod1maxlevel",
    "oldrod1minlevel",
    "oldrod1natid",
    "oldrod2maxlevel",
    "oldrod2minlevel",
    "oldrod2natid",
    "oldrod3maxlevel",
    "oldrod3minlevel",
    "oldrod3natid",
    "oldrod4maxlevel",
    "oldrod4minlevel",
    "oldrod4natid",
    "oldrod5maxlevel",
    "oldrod5minlevel",
    "oldrod5natid",
    "goodrodrate",
    "goodrod1maxlevel",
    "goodrod1minlevel",
    "goodrod1natid",
    "goodrod2maxlevel",
    "goodrod2minlevel",
    "goodrod2natid",
    "goodrod3maxlevel",
    "goodrod3minlevel",
    "goodrod3natid",
    "goodrod4maxlevel",
    "goodrod4minlevel",
    "goodrod4natid",
    "goodrod5maxlevel",
    "goodrod5minlevel",
    "goodrod5natid",
    "superrodrate",
    "superrod1maxlevel",
    "superrod1minlevel",
    "superrod1natid",
    "superrod2maxlevel",
    "superrod2minlevel",
    "superrod2natid",
    "superrod3maxlevel",
    "superrod3minlevel",
    "superrod3natid",
    "superrod4maxlevel",
    "superrod4minlevel",
    "superrod4natid",
    "superrod5maxlevel",
    "superrod5minlevel",
    "superrod5natid",
]
encfmt["platinum"] = encfmt["diamond"][:]
encfmt["heartgold"] = ["BBBBBBxxBBBBBBBBBBBBHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
    +"BBH"*(5*4+2)+"HH",
    "walkrate",
    "surfrate",
    "rocksmashrate",
    "oldrodrate",
    "goodrodrate",
    "superrodrate",
    "walklevel1",
    "walklevel2",
    "walklevel3",
    "walklevel4",
    "walklevel5",
    "walklevel6",
    "walklevel7",
    "walklevel8",
    "walklevel9",
    "walklevel10",
    "walklevel11",
    "walklevel12",
    "walknatidmorning1",
    "walknatidmorning2",
    "walknatidmorning3",
    "walknatidmorning4",
    "walknatidmorning5",
    "walknatidmorning6",
    "walknatidmorning7",
    "walknatidmorning8",
    "walknatidmorning9",
    "walknatidmorning10",
    "walknatidmorning11",
    "walknatidmorning12",
    "walknatidday1",
    "walknatidday2",
    "walknatidday3",
    "walknatidday4",
    "walknatidday5",
    "walknatidday6",
    "walknatidday7",
    "walknatidday8",
    "walknatidday9",
    "walknatidday10",
    "walknatidday11",
    "walknatidday12",
    "walknatidnight1",
    "walknatidnight2",
    "walknatidnight3",
    "walknatidnight4",
    "walknatidnight5",
    "walknatidnight6",
    "walknatidnight7",
    "walknatidnight8",
    "walknatidnight9",
    "walknatidnight10",
    "walknatidnight11",
    "walknatidnight12",
    "hoennnatid1",
    "hoennnatid2",
    "sinnohnatid1",
    "sinnohnatid2",
    "surf1minlevel",
    "surf1maxlevel",
    "surf1natid",
    "surf2minlevel",
    "surf2maxlevel",
    "surf2natid",
    "surf3minlevel",
    "surf3maxlevel",
    "surf3natid",
    "surf4minlevel",
    "surf4maxlevel",
    "surf4natid",
    "surf5minlevel",
    "surf5maxlevel",
    "surf5natid",
    "rocksmash1minlevel",
    "rocksmash1maxlevel",
    "rocksmash1natid",
    "rocksmash2minlevel",
    "rocksmash2maxlevel",
    "rocksmash2natid",
    "oldrod1minlevel",
    "oldrod1maxlevel",
    "oldrod1natid",
    "oldrod2minlevel",
    "oldrod2maxlevel",
    "oldrod2natid",
    "oldrod3minlevel",
    "oldrod3maxlevel",
    "oldrod3natid",
    "oldrod4minlevel",
    "oldrod4maxlevel",
    "oldrod4natid",
    "oldrod5minlevel",
    "oldrod5maxlevel",
    "oldrod5natid",
    "goodrod1minlevel",
    "goodrod1maxlevel",
    "goodrod1natid",
    "goodrod2minlevel",
    "goodrod2maxlevel",
    "goodrod2natid",
    "goodrod3minlevel",
    "goodrod3maxlevel",
    "goodrod3natid",
    "goodrod4minlevel",
    "goodrod4maxlevel",
    "goodrod4natid",
    "goodrod5minlevel",
    "goodrod5maxlevel",
    "goodrod5natid",
    "superrod1minlevel",
    "superrod1maxlevel",
    "superrod1natid",
    "superrod2minlevel",
    "superrod2maxlevel",
    "superrod2natid",
    "superrod3minlevel",
    "superrod3maxlevel",
    "superrod3natid",
    "superrod4minlevel",
    "superrod4maxlevel",
    "superrod4natid",
    "superrod5minlevel",
    "superrod5maxlevel",
    "superrod5natid",
    "radionatid1",
    "radionatid2",
]

def sortentry(s):
    return [s, "H", ["natid"]]
searchfiles = {}
searchfiles["diamond"] = {
    0:["weight","I",["hg"]],
    1:["height","I",["dm"]],
    11:sortentry("national"),
    12:sortentry("regional"),
    13:sortentry("alphabetical"),
    14:sortentry("heaviest"),
    15:sortentry("lightest"),
    16:sortentry("tallest"),
    17:sortentry("smallest"),
    18:sortentry("ABC"),
    19:sortentry("DEF"),
    20:sortentry("GHI"),
    21:sortentry("JKL"),
    22:sortentry("MNO"),
    23:sortentry("PQR"),
    24:sortentry("STU"),
    25:sortentry("VWX"),
    26:sortentry("YZ"),
    27:sortentry("normal"),
    28:sortentry("fighting"),
    29:sortentry("flying"),
    30:sortentry("poison"),
    31:sortentry("ground"),
    32:sortentry("rock"),
    33:sortentry("bug"),
    34:sortentry("ghost"),
    35:sortentry("steel"),
    36:sortentry("fire"),
    37:sortentry("water"),
    38:sortentry("grass"),
    39:sortentry("electric"),
    40:sortentry("psychic"),
    41:sortentry("ice"),
    42:sortentry("dragon"),
    43:sortentry("dark"),
}
searchfiles["platinum"] = searchfiles["diamond"]
searchfiles["heartgold"] = {
    0:["weight","I",["hg"]],
    1:["height","I",["dm"]],
    11:sortentry("national"),
    12:sortentry("regional"),
    13:sortentry("alphabetical"),
    14:sortentry("heaviest"),
    15:sortentry("lightest"),
    16:sortentry("tallest"),
    17:sortentry("smallest"),
    93:sortentry("ABC"),
    94:sortentry("DEF"),
    95:sortentry("GHI"),
    96:sortentry("JKL"),
    97:sortentry("MNO"),
    98:sortentry("PQR"),
    99:sortentry("STU"),
    100:sortentry("VWX"),
    101:sortentry("YZ"),
    62:sortentry("normal"),
    63:sortentry("fighting"),
    64:sortentry("flying"),
    65:sortentry("poison"),
    66:sortentry("ground"),
    67:sortentry("rock"),
    68:sortentry("bug"),
    69:sortentry("ghost"),
    70:sortentry("steel"),
    71:sortentry("fire"),
    72:sortentry("water"),
    73:sortentry("grass"),
    74:sortentry("electric"),
    75:sortentry("psychic"),
    76:sortentry("ice"),
    77:sortentry("dragon"),
    78:sortentry("dark"),
}

DATA_DIR = "local/data/"
STATIC_DIR = "static/"
FORMAT_SUBDIR = "formats/"

POKEDEX_FILE = {
    "diamond":"/poketool/personal/personal.narc",
    "platinum":"/poketool/personal/pl_personal.narc",
    "heartgold":"/a/0/0/2",
    "black":"/a/0/1/6",
    "black2":"/a/0/1/6"
}

EXPRATE_FILE = {
    "diamond":"/poketool/personal/growtbl.narc",
    "platinum":"/poketool/personal/pl_growtbl.narc",
    "heartgold":"/a/0/0/3",
    "black":"/a/0/1/7",
    "black2":"/a/0/1/7",
}

EVO_FILE = {
    "diamond":"/poketool/personal/evo.narc",
    "platinum":"/poketool/personal/evo.narc",
    "heartgold":"/a/0/3/4",
    "black":"/a/0/1/9",
    "black2":"/a/0/1/9",
}

LEVELMOVE_FILE = {
    "diamond":"/poketool/personal/wotbl.narc",
    "platinum":"/poketool/personal/wotbl.narc",
    "heartgold":"/a/0/3/3",
    "black":"/a/0/1/8",
    "black2":"/a/0/1/8",
}

BASEEVO_FILE = {
    "diamond":"/poketool/personal/pms.narc",
    "platinum":"/poketool/personal/pms.narc",
    "heartgold":"/poketool/personal/pms.narc",
    "black":"/a/0/2/0",
    "black2":"/a/0/2/0",
}

TRDATA_FILE = {
    "diamond":"/poketool/trainer/trdata.narc",
    "platinum":"/poketool/trainer/trdata.narc",
    "heartgold":"/a/0/5/5",
    "black":"/a/0/9/2",
    "black2":"/a/0/9/2",
}

TRPOKE_FILE = {
    "diamond":"/poketool/trainer/trpoke.narc",
    "platinum":"/poketool/trainer/trpoke.narc",
    "heartgold":"/a/0/5/6",
    "black":"/a/0/9/3",
    "black2":"/a/0/9/3",
}

ENC_FILE = {
    "diamond":"/fielddata/encountdata/d_enc_data.narc",
    "platinum":"/fielddata/encountdata/pl_enc_data.narc",
    "heartgold":"/a/0/3/7",
    "black":"/a/1/2/6",
    "black2":"/a/1/2/6"
}

MSG_FILE = {
    "diamond":"/msgdata/msg.narc",
    "platinum":"/msgdata/pl_msg.narc",
    "heartgold":"/a/0/2/7",
    "black":"/a/0/0/2",
    "black2":"/a/0/0/2",
}

MSG_FILE2 = {
    "black":"/a/0/0/3",
    "black2":"/a/0/0/3",
}

ZUKAN_FILE = {
    "diamond":"/application/zukanlist/zkn_data/zukan_data.narc",
    "platinum":"/application/zukanlist/zkn_data/zukan_data_gira.narc",
    "heartgold":"/a/0/7/4"
}

for game in games:
    if not os.path.exists(STATIC_DIR+game):
        os.mkdir(STATIC_DIR+game)
    if not os.path.exists(STATIC_DIR+game+"/formats"):
        os.mkdir(STATIC_DIR+game+"/formats")
    if genindex:
        template.idxfile(STATIC_DIR+game+"/index"+FEXT, "w", "Pokemon "+game.title()).close()
        template.idxfile(STATIC_DIR+game+"/formats/index"+FEXT, "w", "Pokemon "+game.title()+" Formats").close()
        
def writefmt(ofile, fmt, datafmt):
    ofs = 0
    padding = 0
    i = 0
    fmt = list(fmt)
    while fmt:
        padding = 0
        while fmt[0] in ('X', 'x'):
            fmt = fmt[1:]
            if not fmt:
                break
            padding += 1
        if padding:
            ofile.write("<tr><td>%d</td><td>%d</td><td>[padding]</td></tr>\n"%(ofs, padding))
            ofs += padding
        if not fmt:
            break
        ofile.write("<tr><td>%d</td><td>%d</td><td>%s</td></tr>\n"%(ofs, struct.calcsize(fmt[0]), datafmt[i]))
        ofs += struct.calcsize(fmt[0])
        fmt = fmt[1:]
        i += 1
        
if __name__ == "__main__":
    import genbaseevo, genenc, genevo, genexprate, genmoves, genpokedex, gentrdata, gentxt, gensearch
    import gennarc, gennclr
    import genfilelist