
import abc


from dispatch.events import Emitter


class BaseInterface(Emitter):
    """Generalized Interface

    This is in charge of creating the actual visual components of the UI

    Events
    ------
    change : (value=mixed)
        Emitted if the value of this interface changes
    trigger : (None)
        Emitted if this interface has been triggered
    okay : (None)
        Emitted if an interface is completed successfully
    cancel : (None)
        Emitted if an interface is completed unsuccessfully
    done : (None)
        Emitted if an interface is completed
    child:add : (child=Interface)
        Emitted when a child is added
    child:remove : (child=Interface)
        Emitted when a child is removed
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
