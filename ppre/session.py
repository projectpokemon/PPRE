
import lang


class Session(object):
    """Class for the passed around session

    There can only be one game open at max per session"""
    def __init__(self, argv):
        self.argv = argv
        self.lang = lang.langs['en']

    def close(self):
        pass
