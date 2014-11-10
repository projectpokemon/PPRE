
import lang


class Session(object):
    """Class for the passed around session

    There can only be one game open at max per session"""
    def __init__(self, argv):
        self.argv = argv
        args = self.argv[1:]
        opt_lang = 'en'
        while args:
            arg = args.pop(0)
            if arg == '--lang':
                opt_lang = args.pop(0)
        self.lang = lang.langs[opt_lang]
        # Session.__setattr__ = self.__setattr__

    def __setattr3__(self, name, value):
        print('but this was called', self.__setattr__)
        object.__setattr__(self, name, value)

    def __setattr2__(self, name, value):
        print('but this was called INSTEAD', self.__setattr__)
        object.__setattr__(self, name, value)

    def close(self):
        pass
