
__all__ = ['temporary_attr']


class TemporaryAttr(object):
    def __init__(self, inst, attr, value, skip_magic=False):
        self.inst = inst
        self.attr = attr
        self.value = value
        self.old = None
        if skip_magic:
            self.setattr = object.__setattr__
            self.getattr = object.__getattribute__
        else:
            self.setattr = setattr
            self.getattr = getattr

    def __enter__(self):
        self.old = self.getattr(self.inst, self.attr)
        self.setattr(self.inst, self.attr, self.value)

    def __exit__(self, type_, value, traceback):
        self.setattr(self.inst, self.attr, self.old)


temporary_attr = TemporaryAttr  # Export as function
