
from ppre.ui.base_ui import BaseUserInterface


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

    def new(self):
        pass

    def open(self):
        pass

    def save(self):
        pass

    def save_as(self):
        pass

    def export(self):
        pass

    def export_as(self):
        pass

    def quit(self):
        exit()
