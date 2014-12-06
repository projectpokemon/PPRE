
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
            with self.prompt('should_save') as prompt:
                # TODO: Yes/No
                prompt.message('project_changed_save')

                @prompt.on('okay')
                def okay(evt):
                    self.save()  # TODO: handle non-blocking case?
                    self['should_save'].destroy()
                    func(self, *args, **kwargs)

                @prompt.on('cancel')
                def done(evt):
                    self['should_save'].destroy()
                    func(self, *args, **kwargs)
        else:
            func(self, *args, **kwargs)
    return wrapper


class HomeUserInterface(BaseUserInterface):
    def __init__(self, ui, session):
        super(HomeUserInterface, self).__init__(ui, 'home', session)
        self.title('PPRE 5.0')
        self.icon('PPRE.ico')
        with self.menu('file') as file_menu:
            file_menu.action('new', self.new,
                             file_menu.shortcut('n', ctrl=True))
            file_menu.action('open', self.open,
                             file_menu.shortcut('o', ctrl=True))
            file_menu.action('save', self.save,
                             file_menu.shortcut('s', ctrl=True))
            file_menu.action('save_as', self.save_as,
                             file_menu.shortcut('s', ctrl=True, shift=True))
            file_menu.action('export', self.export,
                             file_menu.shortcut('e', ctrl=True))
            file_menu.action('export_as', self.export_as,
                             file_menu.shortcut('e', ctrl=True, shift=True))
            file_menu.action('quit', self.quit,
                             file_menu.shortcut('q', ctrl=True))

        with self.menu('tools') as tools_menu:
            tools_menu.action('edit_pokemon', self.edit_pokemon)

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
        self.set_game(Game())
        self.bind('rom', self.session, 'game')

    def set_game(self, game):
        self.session.game = game
        self.title('PPRE 5.0 - {0}'.format(game.game_name), color=game.color)

    @confirm
    def new(self):
        with self.prompt('open') as prompt:
            prompt.file('file', types=['NDS Files (*.nds)',
                                       '3DS Files (*.3ds *.3dz)',
                                       'All Files (*.*)'])
            prompt.file('parent_directory', directory=True)
            prompt['parent_directory'].set_value('')
            prompt.boolean('backup')

            @prompt.on('okay')
            def okay(evt):
                print('Okay')
                target = prompt['file'].get_value()
                directory = prompt['parent_directory'].get_value()
                backup = prompt['backup'].get_value()
                self['open'].destroy()
                if not target:
                    return
                if not directory:
                    directory = os.path.dirname(target)
                tail = os.path.split(target)[1]
                name, ext = os.path.splitext(tail)
                ext = ext.lower()
                directory = os.path.join(directory, name)
                try:
                    os.mkdir(directory)
                except OSError:
                    with self.prompt('replace_dir') as replace_prompt:
                        replace_prompt.should_replace = False
                        replace_prompt.message('should_replace_dir')

                        @replace_prompt.on('okay')
                        def okay(evt):
                            replace_prompt.should_replace = True
                            shutil.rmtree(directory)
                            os.mkdir(directory)
                            self['replace_dir'].destroy()

                        @replace_prompt.on('cancel')
                        def cancel(evt):
                            self['replace_dir'].destroy()
                    if not replace_prompt.should_replace:
                        return
                self.set_game(Game.from_file(target, directory))
                base_file = target
                if backup:
                    base_file = os.path.join(self.session.game.files.directory,
                                             tail)
                    shutil.copy(target, base_file)
                self.session.game.files.base = base_file
                self.session.game.write_config()

            @prompt.on('cancel')
            def cancel(evt):
                print('Cancelled')
                self['open'].destroy()
            prompt.focus('file')

    @confirm
    def open(self):
        with self.prompt('open', hide=True) as prompt:
            file = prompt.file('file', types=['PPRE Projects (*.pprj)'])

            @file.on('okay')
            def okay(evt):
                prompt.fire('okay')

            @file.on('cancel')
            def cancel(evt):
                prompt.fire('cancel')

            @prompt.on('okay')
            def okay(evt):
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
                self.set_game(game)
                self.save_hash = self.session.game.checksum()
                self.save_filename = target

            @prompt.on('cancel')
            def cancel(evt):
                self['open'].destroy()
            prompt.focus('file')

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
                self.session.game.write_config()
                parser.write(handle)
            self.save_hash = self.session.game.checksum()
        else:
            try:
                self.save_as()
            except:
                pass

    def save_as(self):
        with self.prompt('open', hide=True) as prompt:
            prompt.file('file', types=['PPRE Projects (*.pprj)'], new=True)
            # TODO: hook on event and fires
            # TODO: Get rid of this patch
            # TODO: Handle cancel action in dialog
            prompt['file'].set_value = prompt['file'].ui.set_value = \
                hook.multi_call_patch(prompt['file'].set_value)
            prompt['file'].set_value.add_call(
                lambda res, value: res.noop(prompt.fire('okay')))

            @prompt.on('okay')
            def okay(evt):
                target = prompt['file'].get_value()
                self['open'].destroy()
                if not target:
                    return
                self.save_filename = target
                self.save()

            @prompt.on('cancel')
            def cancel(evt):
                self['open'].destroy()
            prompt.focus('file')

    def export(self):
        print(self.session.game.to_json())

    def export_as(self):
        pass

    @confirm
    def quit(self):
        exit()

    def edit_pokemon(self):
        from ppre.ui.editpokemon import PokemonUserInterface

        PokemonUserInterface(self.ui.new(), self.session).show()
