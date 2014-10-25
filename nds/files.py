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

MOVEDATA_FILE = {
    "diamond":"/poketool/waza/waza_tbl.narc",
    "platinum":"/poketool/waza/pl_waza_tbl.narc",
    "heartgold":"/a/0/1/1",
    "black":"/a/0/2/1",
    "black2":"/a/0/2/1"
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

ITEMDATA_FILE = {
    "diamond":"/itemtool/itemdata/item_data.narc",
    "platinum":"/itemtool/itemdata/pl_item_data.narc",
    "heartgold":"/a/0/1/7",
    "black":"/a/0/2/4",
    "black2":"/a/0/2/4"
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
    "heartgold":"/a/0/7/4",
    "black":"/a/0/2/1",
} 

def getFSHTML(FEXT):
    return {
    "diamond":{
        "/poketool/personal/personal.narc":"<a href='pokedex"+FEXT+"'>Pokemon data</a>",
        "/poketool/personal/growtbl.narc":"<a href='exprate"+FEXT+"'>Experience Table</a>",
        "/poketool/personal/evo.narc":"<a href='evo"+FEXT+"'>Evolutions</a>",
        "/poketool/personal/wotbl.narc":"<a href='levelmoves"+FEXT+"'>Level-Up Moves</a>",
        "/poketool/waza/waza_tbl.narc":"<a href='movedata"+FEXT+"'>Move Data</a>",
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
        "/poketool/waza/pl_waza_tbl.narc":"<a href='movedata"+FEXT+"'>Move Data</a>",
        "/poketool/personal/pms.narc":"<a href='baseevo"+FEXT+"'>Base Evolutions/Baby Pokemon</a>",
        "/poketool/trainer/trdata.narc":"<a href='trdata"+FEXT+"'>Trainer data</a>",
        "/fielddata/encountdata/pl_enc_data.narc":"<a href='enc"+FEXT+"'>Encounter Data</a>",
        "/msgdata/pl_msg.narc":"<a href='msg"+FEXT+"'>Text/Message Files</a>",
        "/application/zukanlist/zukan_data/zukan_data_gira.narc":"<a href='search"+FEXT+"'>Dex Search Files</a>",
        
        "/poketool/personal/personal.narc":"DP Pokemon Data",
        "/poketool/personal/growtbl.narc":"DP Experience Table",
        "/poketool/waza/waza_tbl.narc":"DP Move Data",
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
        "/a/0/1/1":"<a href='movedata"+FEXT+"'>Move Data</a>",
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
        "/a/0/2/1":"<a href='movedata"+FEXT+"'>Move Data</a>",
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
        "/a/0/2/1":"<a href='movedata"+FEXT+"'>Move Data</a>",
        "/a/0/1/9":"<a href='evo"+FEXT+"'>Evolutions</a>",
        "/a/0/2/0":"<a href='baseevo"+FEXT+"'>Base Evolutions/Baby Pokemon</a>",
        "/a/0/9/2":"<a href='trdata"+FEXT+"'>Trainer data</a>",
        "/a/1/2/6":"Encounter Data",
        
        },
}