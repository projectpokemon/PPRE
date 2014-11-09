
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

    def close(self):
        pass
