
import os

from ppre.ui.bind import Bind


ALL_PARENTS = object()


def ui_wrap(method, doc=''):

    def func(self, name, *args, **kwargs):
        text = self.translate(name)
        ui = getattr(self.ui, method)(text, *args, **kwargs)
        return BaseUserInterface(ui, name, self.session, self)
    func.__name__ = method
    func.__doc__ = doc
    return func


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
        self.bindings = []  # Multi-dict
        if self.parent is not None:
            if name in self.parent.children:
                raise ValueError('{parent} already has a {name}'.format(
                    parent=self.parent, name=self.name))
            self.parent.children[name] = self
        self.get_value = self.ui.get_value
        self.set_value = self.ui.set_value

    def show(self):
        self.ui.show()

    def translate(self, text):
        path = [text]
        parent = self
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        entry = self.session.lang.table
        try:
            for p in path:
                entry = entry[p]
        except:
            entry = text
        return str(entry)

    def bind(self, key, parent=None, attr=None, unbind=True):
        old_parents = []
        already_bound = False
        for bkey, binding in self.bindings:
            if bkey == key:
                if binding.parent == parent:
                    already_bound = True
                    continue
                elif unbind:
                    old_parents.append(binding.parent)
        for old_parent in old_parents:
            self.unbind(key, old_parent)
        if already_bound:
            return
        self.bindings.append((key,
                              Bind(self, key, parent, attr, unbind=unbind)))

    def unbind(self, key, parent=ALL_PARENTS):
        bindings = []
        for entry in self.bindings:
            if entry[0] == key:
                if parent is ALL_PARENTS or entry[1].parent == parent:
                    entry[1].unbind()
                    continue
            bindings.append(entry)
        self.bindings = bindings

    def destroy(self):
        self.ui.destroy()
        if self.parent is not None:
            del self.parent[self.name]

    def new(self, cls=None):
        """Return a new interface"""
        ui = self.ui.new()
        if cls is None:
            cls = BaseUserInterface
        return cls(ui, None, self.session, None)

    def focus(self, name):
        """Focus on a particular component by name"""
        self.ui.focus(self[name].ui)

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

    boolean = ui_wrap('boolean')

    def browse(self, name, *args, **kwargs):
        text = self.translate(name)
        ui = self.ui.browse(text, *args, **kwargs)
        return BaseUserInterface(ui, name, self.session, self)

    file = ui_wrap('file')

    def prompt(self, name, *args, **kwargs):
        text = self.translate(name)
        ui = self.ui.prompt(text, *args, **kwargs)
        bui = BaseUserInterface(ui, name, self.session, self)
        # TODO: hook and fire events
        bui.on_okay = ui.on_okay
        bui.on_cancel = ui.on_cancel
        bui.okay = ui.okay
        bui.cancel = ui.cancel
        return bui

    def title(self, name, color=None):
        """Set the title"""
        self.ui.title(name, color)

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

    def __delitem__(self, name):
        del self.children[name]

    def keys(self):
        return self.children.keys()

    def __contains__(self, item):
        return item in self.children

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.show()


if __name__ == '__main__':
    # Build documentation typing
    from ppre.interface import BaseInterface
    from ppre.session import Session

    session = Session()
    BaseUserInterface(BaseInterface(session), 'interface', session)
