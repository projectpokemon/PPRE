
import functools

from ppre.ui.base_ui import BaseUserInterface
from pokemon.game import Game


def confirm(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        print(self.save_hash)
        if self.save_hash and (self.save_hash != self.session.game.checksum()):
            print('Save first')
        else:
            func(self, *args, **kwargs)
    return wrapper


class HomeUserInterface(BaseUserInterface):
    def __init__(self, ui, session):
        super(HomeUserInterface, self).__init__(ui, 'home', session)
        self.title('PPRE 5.0')
        self.icon('PPRE.ico')
        with self.menu('file') as file_menu:
            file_menu.action('new', self.new)
            file_menu.action('open', self.open)
            file_menu.action('save', self.save)
            file_menu.action('save_as', self.save_as)
            file_menu.action('export', self.export)
            file_menu.action('export_as', self.export_as)
            file_menu.action('quit', self.quit)

        with self.group('rom') as rom_group:
            with rom_group.group('files') as files_group:
                files_group.edit('base')
                files_group.edit('directory')
            with rom_group.group('project') as project_group:
                project_group.edit('name')
                project_group.edit('description', soft_rows=4)
                project_group.edit('version')
                project_group.edit('output')
        self.clear()
        self.save_hash = self.session.game.checksum()

    def clear(self):
        self.session.game = Game()
        self.bind('rom', self.session, 'game')

    @confirm
    def new(self):
        with self.prompt('open') as prompt:
            prompt.file('file', types=['NDS Files (*.nds)',
                                       '3DS Files (*.3ds)',
                                       'All Files (*.*)'])
            prompt.focus('file')

        @prompt.okay
        def okay():
            print('Okay')
            target = prompt['file'].get_value()
            if not target:
                return
            self.session.game = Game.from_file(target)
            self['open'].destroy()

        @prompt.cancel
        def cancel():
            print('Cancelled')
            self['open'].destroy()

    @confirm
    def open(self):
        print(self.session.game.project.name)

    def save(self):
        self.save_hash = self.session.game.checksum()
        pass

    def save_as(self):
        pass

    def export(self):
        print(self.session.game.to_json())

    def export_as(self):
        pass

    @confirm
    def quit(self):
        exit()
