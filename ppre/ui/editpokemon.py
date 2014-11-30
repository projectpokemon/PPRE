
from ppre.ui.base_ui import BaseUserInterface
from pokemon import Pokemon
from pokemon.poketool.personal import Stats


class PokemonUserInterface(BaseUserInterface):
    def __init__(self, ui, session):
        super(PokemonUserInterface, self).__init__(ui, 'pokemon', session)
        self.title('Pokemon Editor', color=session.game.color)
        self.data = Pokemon(session.game)
        with self.group('pokemon') as pokemon_group:
            natid = self.edit('natid')

            @natid.on('changed')
            def natid_changed(evt):
                print(evt.data.value, )
            with pokemon_group.group('personal') as personal_group:
                with personal_group.group('base_stat') as base_stat_group:
                    for stat in Stats.STATS:
                        base_stat_group.edit(stat)
                personal_group.edit('catchrate')
                personal_group.edit('baseexp')
                with personal_group.group('evs') as evs_group:
                    for stat in Stats.STATS:
                        evs_group.edit(stat)
                personal_group.edit('gender')
                personal_group.edit('hatchsteps')
                personal_group.edit('happiness')
                personal_group.edit('growth')
                personal_group.edit('flee')
                personal_group.edit('color')
            with pokemon_group.group('evolutions') as evolutions_group:
                with evolutions_group.group('0') as group_0:
                    group_0.edit('method')
                    group_0.edit('parameter')
                    group_0.edit('target')
            with pokemon_group.group('levelmoves') as levelmoves_group:
                with levelmoves_group.group('0') as group_0:
                    group_0.edit('moveid')
                    group_0.edit('level')
        self.bind('pokemon', self, 'data')
