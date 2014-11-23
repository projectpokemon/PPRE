
stats = {'hp': 'HP', 'attack': 'Attack', 'defense': 'Defense',
         'speed': 'Speed', 'spatk': 'Special Attack',
         'spdef': 'Special Defense'}

table = {
    '_': 'Pokemon',
    'pokemon': {
        '_': 'Pokemon',
        'natid': 'National ID',
        'personal': {
            '_': 'Personal Data',
            'base_stat': dict(_='Base Stats', **stats),
            'evs': dict(_='EVs', **stats),
        }
    }
}
