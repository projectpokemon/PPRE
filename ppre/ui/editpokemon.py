
from ppre.ui.base_ui import BaseUserInterface
from pokemon import Pokemon
from pokemon.poketool.personal import Stats


class PokemonUserInterface(BaseUserInterface):
    def __init__(self, ui, session):
        super(PokemonUserInterface, self).__init__(ui, 'pokemon', session)
        self.title('Pokemon Editor', color=session.game.color)
        self.data = Pokemon(session.game)
        with self.menu('file') as file_menu:
            file_menu.action('new', self.new,
                             file_menu.shortcut('n', ctrl=True))
            file_menu.action('save', self.save,
                             file_menu.shortcut('s', ctrl=True))
            file_menu.action('save_as', self.save_as,
                             file_menu.shortcut('s', ctrl=True, shift=True))
            file_menu.action('export', self.export,
                             file_menu.shortcut('e', ctrl=True))
            file_menu.action('export_as', self.export_as,
                             file_menu.shortcut('e', ctrl=True, shift=True))
            file_menu.action('close', self.close,
                             file_menu.shortcut('w', ctrl=True))
        """with self.group('pokemon') as pokemon_group:
            natid = self.edit('natid')

            @natid.on('changed')
            def natid_changed(evt):
                print(evt.data.value, )
            with pokemon_group.group('personal') as personal_group:
                with personal_group.group('base_stat') as base_stat_group:
                    for stat in Stats.STATS:
                        base_stat_group.edit(stat)
                personal_group.number('catchrate')
                personal_group.number('baseexp')
                with personal_group.group('evs') as evs_group:
                    for stat in Stats.STATS:
                        evs_group.number(stat)
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
                    group_0.edit('level')"""
        with self.group('pokemon') as pokemon_group:
            self.update_from_data(self.data, pokemon_group)

        natid = self['pokemon']['natid']

        @natid.on('changed')
        def natid_changed(evt):
            self.load(evt.data.value)

        print('prebind', self.data)
        self.bind('pokemon', self, 'data')
        print(self.data)

    def load(self, natid):
        self.data.load_id(natid)

    def new(self):
        pass

    def save(self):
        pass

    def save_as(self):
        pass

    def export(self):
        pass

    def export_as(self):
        pass

    def close(self):
        self.destroy()
