
from lang.lang import Table

stats = {'hp': 'HP', 'attack': 'Attack', 'defense': 'Defense',
         'speed': 'Speed', 'spatk': 'Special Attack',
         'spdef': 'Special Defense'}

table = {
    '_': 'Pokemon',
    'file': Table('en.home')['file'],
    'pokemon': {
        '_': 'Pokemon',
        'natid': 'National ID',
        'personal': {
            '_': 'Personal Data',
            'base_stat': dict(_='Base Stats', **stats),
            'evs': dict(_='EVs', **stats),
            'catchrate': 'Catch Rate',
            'baseexp': 'Base Exp.',
            'gender': 'Gender',
            'hatchsteps': 'Hatch Cycles',
            'happiness': 'Happiness',
            'growth': 'Growth',
            'flee': 'Flee',
            'color': 'Color'
        },
        'evolutions': {
            '_': 'Evolutions'
        },
        'levelmoves': {
            '_': 'Level-Up Moves'
        }
    }
}
