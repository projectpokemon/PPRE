
from ppre.gui.interface import Interface

from file import FileInterface
from edit import EditInterface, NumberInterface

__all__ = ['FileInterface', 'PromptInterface', 'BooleanInterface',
           'EditInterface', 'NumberInterface']


class PromptInterface(Interface):
    def destroy(self):
        self.widget.close()


class BooleanInterface(Interface):
    def get_value(self):
        if self.widget.isChecked():
            return True
        else:
            return False

    def set_value(self, value):
        if value:
            if not self.get_value():
                self.widget.setChecked(True)
        else:
            if self.get_value():
                self.widget.setChecked(False)
