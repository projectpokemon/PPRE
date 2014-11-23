
stats = {'hp': 'Vita', 'attack': 'Impetus', 'defense': 'Praesidium',
         'speed': 'Celeritas', 'spatk': 'Impetus Magus',
         'spdef': 'Praesidium Magum'}

table = {
    '_': 'Pokemon',
    'pokemon': {
        '_': 'Pokemon',
        'natid': 'Numerus Civis',
        'personal': {
            '_': 'Data Sua',
            'base_stat': dict(_='Census Priori', **stats),
            'evs': dict(_='Pretia Laboris', **stats),
            'catchrate': 'Regula Capturae',
            'baseexp': 'Exp. Prior',
            'gender': 'Sexus',
            'hatchsteps': 'Tempus Nativitas',
            'happiness': 'Felicitas',
            'growth': 'Incrementum',
            'flee': 'Fugis',
            'color': 'Color'
        },
        'evolutions': {
            '_': 'Praegressi'
        },
        'levelmoves': {
            '_': 'Artes Adolescentes'
        }
    }
}
