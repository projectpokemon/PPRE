
import struct

from rawdb.elements.atom.atomic import AtomicInstance
from rawdb.elements.atom.packer import Packer
from rawdb.elements.atom.data import DataConsumer
from rawdb.elements.atom.valence import ValenceFormatter, ValenceArray, \
    ValenceMulti, ValenceSeek


class BaseAtom(Packer):
    """Base class for single element entries.

    This is used to read and build data formats.

    """
    atomic = AtomicInstance
    subatomic = AtomicInstance

    def __init__(self):
        self._fmt = []
        self._subfmts = []

    def __call__(self, data):
        if self._subfmts:
            raise RuntimeError('Subatoms have not returned fully')
        data = DataConsumer(data)
        atomic = self.atomic(self, data)
        unpacked = {}
        for entry in self.format_iterator(atomic):
            value = entry.unpack_one(atomic)
            if not entry.ignore:
                atomic[entry.name] = value
        atomic.freeze()
        return atomic

    def keys(self):
        return [entry.name for entry in self._fmt if entry.name]

    def format_iterator(self, atomic):
        return self._fmt

    def int8(self, name):
        """Parse named field as int8

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(ValenceFormatter(name, 'b'))

    def uint8(self, name):
        """Parse named field as uint8

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(ValenceFormatter(name, 'B'))

    def int16(self, name):
        """Parse named field as int16

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(ValenceFormatter(name, 'h'))

    def uint16(self, name):
        """Parse named field as uint16

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(ValenceFormatter(name, 'H'))

    def int32(self, name):
        """Parse named field as int32

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(ValenceFormatter(name, 'i'))

    def uint32(self, name):
        """Parse named field as uint32

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(ValenceFormatter(name, 'I'))

    def string(self, name, count):
        if hasattr(count, '__call__'):
            format_char = lambda atomic: '%ds' % count(atomic)
        else:
            format_char = '%ds' % count
        formatter = self.append_format(ValenceFormatter(name, format_char))
        return formatter
    data = string

    def padding(self, length):
        entry = ValenceFormatter(None, 'x'*length)
        entry.ignore = True
        return self.append_format(entry)

    def array(self, format_entry, count=None, terminator=None):
        """Parse field array

        Parameters
        ----------
        name : string
            Name of field
        format_entry
            Formatter (result of self.int8(name), etc)
        count : int, function, or None
            if not None, array stops growing at this size.
        terminator : int or None
            if not None, array stops when a value matching this shows up.
        """
        new_entry = ValenceArray(format_entry.name, format_entry, count,
                                 terminator)
        return self.replace_format(format_entry, new_entry, pop=False)

    def seek(self, offset, start=None):
        return self.append_format(ValenceSeek(offset, start))

    def sub_push(self, name):
        self._subfmts.append((name, self._fmt))
        self._fmt = []

    def sub_pop(self):
        sub_fmt = self._fmt
        name, self._fmt = self._subfmts.pop()
        format_entry = ValenceMulti(name, sub_fmt)
        format_entry.subatomic = self.subatomic
        return self.append_format(format_entry)

    def append_format(self, formatter):
        """Add a new format entry

        Parameters
        ----------
        name : string
            Field name
        formatter : ValenceFormatter
            Describes how to format a section of data.

        Returns
        -------
        formatter : ValenceFormatter
            Format entry
        """
        self._fmt.append(formatter)
        return formatter

    def replace_format(self, old_ref, new_entry, pop=True):
        """Replace an old format entry with a new one

        Parameters
        ----------
        old_ref : string or ValenceFormatter
            Item to replace
        new_entry : ValenceFormatter
            New format entry
        pop : bool
            If pop is True, remove new_entry from format list
        """
        if pop:
            self.remove_format(new_entry)
        if isinstance(old_ref, ValenceFormatter):
            index = self._fmt.index(old_ref)
            self._fmt[index] = new_entry
        else:
            self._fmt = [new_entry if fmt.name == old_ref else fmt
                         for fmt in self._fmt]
        return new_entry

    def remove_format(self, old_ref):
        """Remove a format entry by reference

        Parameters
        ----------
        old_ref : string or ValenceFormatter
            Reference to item or item's name to remove
        """
        if isinstance(old_ref, ValenceFormatter):
            self._fmt.remove(old_ref)
        else:
            self._fmt = [fmt for fmt in self._fmt if fmt.name != old_ref]

    def pop_format(self, index=-1):
        """Pops off the last (or specified) formatter

        Paramters
        ---------
        index : int, optional
            Index to remove

        Returns
        -------
        formatter : ValenceFormatter
            Popped formatter
        """
        return self._fmt.pop(index)
