
import importlib


class TableEntry(object):
    def __init__(self, entry):
        self.entry = entry

    def __getattr__(self, name):
        return TableEntry(self.entry[name])

    def __getitem__(self, name):
        return getattr(self, name)

    def __str__(self):
        try:
            entry = self.entry['_']
        except:
            entry = self.entry
        return str(entry)


class Table(object):
    base_path = 'lang.'

    def __init__(self, path):
        self.path = path
        self.module = None

    def load(self):
        if self.module is None:
            self.module = importlib.import_module(self.base_path+self.path)
            self.table = self.module.table

    def __getattr__(self, name):
        self.load()
        return TableEntry(self.table[name])

    def __getitem__(self, name):
        return getattr(self, name)


class Language(object):
    langs = {}

    def __init__(self, name):
        self.name = name
        self.table = Table(self.name)
        Language.langs[self.name] = self

    def build(self):
        pass
