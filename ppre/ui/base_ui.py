

class BaseUserInterface(object):
    """Base Interface wrapper

    This defers all items to the ui
    """
    def __init__(self, ui, session, parent=None):
        self.ui = ui
        self.session = session
        self.parent = parent

    def show(self):
        self.ui.show()

    def translate(self, text):
        # TODO
        return text

    def menu(self, name):
        """Add a menu

        Menus should be added before content
        """
        text = self.translate(name)
        ui = self.ui.menu(text)
        return BaseUserInterface(ui, self.session, self)

    def action(self, name, callback):
        """Add an action item to a menu"""
        text = self.translate(name)
        ui = self.ui.action(text, callback)
        return BaseUserInterface(ui, self.session, self)

    def group(self, name):
        """Create a tool group for logically indivisible components"""
        text = self.translate(name)
        ui = self.ui.group(text)
        return BaseUserInterface(ui, self.session, self)

    def edit(self, name, *args, **kwargs):
        text = self.translate(name)
        ui = self.ui.edit(text, *args, **kwargs)
        return BaseUserInterface(ui, self.session, self)

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.show()
