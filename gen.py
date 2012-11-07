#!/usr/bin/env python
import os, sys
import struct

allowed_games = ["diamond", "platinum", "heartgold"]

games = []
for a in sys.argv[1:]:
    if a == "--help":
        print("Usage: %s [%s]\
If game is left blank, all games will be processed."%(sys.argv[0], "|".join(allowed_games)))
        exit()
    if a in allowed_games:
        games.append(a)
if not games:
    games = allowed_games

struct_name = {"B": "UInt8", "H":"UInt16", "I":"UInt32"}

FEXT = ".php"

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
        
        "/poketool/personal/personal.narc":"DP Pokemon Data",
        "/poketool/personal/growtbl.narc":"DP Experience Table",
        "/fielddata/encountdata/d_enc_data.narc":"Diamond Encounter Data",
        "/fielddata/encountdata/p_enc_data.narc":"Pearl Encounter Data",
        "/msgdata/msg.narc":"DP Message Files",
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

movefmt = {}
movefmt["diamond"] = ["H",
    ["moveid", 0, 8, 0x1FF],
    ["level", 9, 15, 0x7F],
]
movefmt["platinum"] = movefmt["diamond"][:]
movefmt["heartgold"] = movefmt["diamond"][:]

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

trpokefmt = {
    "diamond":["HHHHHHHxx",
    ["level"],
    ["formepokemon"],
    ["itemmove1"],
    ["move2"],
    ["move3"],
    ["move4"],
    ["replacedmove1"]
    ],
}

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
# TODO: heartgold

DATA_DIR = "local/data/"
STATIC_DIR = "static/"
FORMAT_SUBDIR = "formats/"

POKEDEX_FILE = {
    "diamond":"/poketool/personal/personal.narc",
    "platinum":"/poketool/personal/pl_personal.narc",
    "heartgold":"/a/0/0/2"
}

EXPRATE_FILE = {
    "diamond":"/poketool/personal/growtbl.narc",
    "platinum":"/poketool/personal/pl_growtbl.narc",
    "heartgold":"/a/0/0/3"
}

EVO_FILE = {
    "diamond":"/poketool/personal/evo.narc",
    "platinum":"/poketool/personal/evo.narc",
    "heartgold":"/a/0/3/4"
}

LEVELMOVE_FILE = {
    "diamond":"/poketool/personal/wotbl.narc",
    "platinum":"/poketool/personal/wotbl.narc",
    "heartgold":"/a/0/3/3"
}

BASEEVO_FILE = {
    "diamond":"/poketool/personal/pms.narc",
    "platinum":"/poketool/personal/pms.narc",
    "heartgold":"/poketool/personal/pms.narc",
}

TRDATA_FILE = {
    "diamond":"/poketool/trainer/trdata.narc",
    "platinum":"/poketool/trainer/trdata.narc",
    "heartgold":"/a/0/5/5"
}

TRPOKE_FILE = {
    "diamond":"/poketool/trainer/trpoke.narc",
    "platinum":"/poketool/trainer/trpoke.narc",
    "heartgold":"/a/0/5/6"
}

ENC_FILE = {
    "diamond":"/fielddata/encountdata/d_enc_data.narc",
    "platinum":"/fielddata/encountdata/pl_enc_data.narc",
    "heartgold":"/a/0/3/7"
}

MSG_FILE = {
    "diamond":"/msgdata/msg.narc",
    "platinum":"/msgdata/pl_msg.narc",
    "heartgold":"/a/0/2/7"
}

for game in games:
    if not os.path.exists(STATIC_DIR+game):
        os.mkdir(STATIC_DIR+game)
    if not os.path.exists(STATIC_DIR+game+"/formats"):
        os.mkdir(STATIC_DIR+game+"/formats")
        
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
    import genbaseevo, genenc, genevo, genexprate, genmoves, genpokedex, gentrdata, gentxt
    import genfilelist