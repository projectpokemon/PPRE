
import os

from ppre.ui.bind import Bind


class BaseUserInterface(object):
    """Base Interface wrapper

    This defers all items to the ui
    """
    def __init__(self, ui, name, session, parent=None):
        self.ui = ui
        self.name = name
        self.session = session
        self.parent = parent
        self.children = {}
        self.bindings = []
        if self.parent is not None:
            if name in self.parent.children:
                raise ValueError('{parent} already has a {name}'.format(
                    parent=self.parent, name=self.name))
            self.parent.children[name] = self

    def show(self):
        self.ui.show()

    def translate(self, text):
        path = [text]
        parent = self
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        entry = self.session.lang.table
        for p in path:
            entry = entry[p]
        return str(entry)

    def get_value(self):
        # Provide thin getters for easy overriding
        return self.ui.value

    def set_value(self, new_value):
        self.ui.value = new_value
    value = property(lambda self: self.get_value(),
                     lambda self, new_value: self.set_value(new_value))

    def bind(self, container, key, model=None, attr=None):
        self.bindings.append(Bind(container, key, model, attr))

    def menu(self, name):
        """Add a menu

        Menus should be added before content
        """
        text = self.translate(name)
        ui = self.ui.menu(text)
        return BaseUserInterface(ui, name, self.session, self)

    def action(self, name, callback):
        """Add an action item to a menu"""
        text = self.translate(name)
        ui = self.ui.action(text, callback)
        return BaseUserInterface(ui, name, self.session, self)

    def group(self, name):
        """Create a tool group for logically indivisible components"""
        text = self.translate(name)
        ui = self.ui.group(text)
        return BaseUserInterface(ui, name, self.session, self)

    def edit(self, name, *args, **kwargs):
        text = self.translate(name)
        ui = self.ui.edit(text, *args, **kwargs)
        return BaseUserInterface(ui, name, self.session, self)

    def title(self, name):
        """Set the title"""
        self.ui.title(name)

    def icon(self, filename, relative=True):
        """Set the title"""
        if relative:
            filename = os.path.join(os.path.dirname(__file__), '../../',
                                    filename)
        self.ui.icon(filename)

    def __getitem__(self, name):
        return self.children[name]

    def __setitem__(self, key, value):
        self.children[key] = value

    def keys(self):
        return self.children.keys()

    def __contains__(self, item):
        return item in self.children

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.show()
