
import abc


class BaseInterface(object):
    """Generalized Interface

    This is in charge of creating the actual visual components of the UI
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, session):
        self.session = session

    @staticmethod
    def shortcut(self, char, ctrl=False, shift=False, alt=False, meta=False):
        return None

    def menu(self, text):
        return BaseInterface(self.session)

    def action(self, text, callback):
        return BaseInterface(self.session)

    def group(self, text):
        return BaseInterface(self.session)

    def show(self):
        pass
