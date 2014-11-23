
import functools
import os
import shutil

from six.moves import configparser

from ppre.ui.base_ui import BaseUserInterface
from pokemon.game import Game
from util import hook


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
        self.save_filename = None

    def clear(self):
        self.session.game = Game()
        self.bind('rom', self.session, 'game')

    @confirm
    def new(self):
        with self.prompt('open') as prompt:
            prompt.file('file', types=['NDS Files (*.nds)',
                                       '3DS Files (*.3ds)',
                                       'All Files (*.*)'])
            prompt.file('parent_directory', directory=True)
            prompt['parent_directory'].set_value('')
            prompt.boolean('backup')
            prompt.focus('file')

        @prompt.on_okay
        def okay():
            print('Okay')
            target = prompt['file'].get_value()
            directory = prompt['parent_directory'].get_value()
            if not target:
                return
            if not directory:
                directory = os.path.dirname(target)
            # TODO: Confirm directory overwrite?
            self.session.game = Game.from_file(target, directory)
            base_file = target
            if prompt['backup'].get_value():
                base_file = os.path.split(target)[1]
                base_file = os.path.join(self.session.game.files.directory,
                                         base_file)
                shutil.copy(target, base_file)
            self.session.game.files.base = base_file
            self.session.game.write_config()
            self['open'].destroy()

        @prompt.on_cancel
        def cancel():
            print('Cancelled')
            self['open'].destroy()

    @confirm
    def open(self):
        with self.prompt('open') as prompt:
            prompt.file('file', types=['PPRE Projects (*.pprj)'])
            # TODO: hook on event and fires
            # TODO: Get rid of this patch
            # TODO: Handle cancel action in dialog
            prompt['file'].set_value = prompt['file'].ui.set_value = \
                hook.multi_call_patch(prompt['file'].set_value)
            prompt['file'].set_value.add_call(
                lambda res, value: res.noop(prompt.okay()))
            prompt.focus('file')

        @prompt.on_okay
        def okay():
            target = prompt['file'].get_value()
            self['open'].destroy()
            if not target:
                return
            with open(target) as handle:
                parser = configparser.ConfigParser()
                parser.readfp(handle)
            try:
                # Compat with PPRE2
                workspace = parser.get('files', 'workspace')
                game = Game.from_workspace(workspace)
            except configparser.NoSectionError as nse:
                try:
                    workspace = parser.get('location', 'directory')
                except:
                    raise nse
                game = Game.from_workspace(workspace)
                game.files.from_dict(dict(parser.items('location')))
                game.project.from_dict(dict(parser.items('project')))
                game.write_config()
            self.session.game = game
            self.save_hash = self.session.game.checksum()
            self.save_filename = target

        @prompt.on_cancel
        def cancel():
            self['open'].destroy()

    def save(self):
        if self.save_filename:
            with open(self.save_filename, 'w') as handle:
                parser = configparser.ConfigParser()
                try:
                    parser.add_section('files')
                except configparser.DuplicateSectionError:
                    pass
                parser.set('files', 'workspace',
                           self.session.game.files.directory)
                parser.write(handle)
        self.save_hash = self.session.game.checksum()

    def save_as(self):
        pass

    def export(self):
        print(self.session.game.to_json())

    def export_as(self):
        pass

    @confirm
    def quit(self):
        exit()
