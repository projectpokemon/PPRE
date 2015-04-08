"""This module aids in the creation of executables that can be disassembled
with added symbols. These executables are not meant to actually be run.

The typical target is ARM9.bin
"""

from util.io import BinaryIO
from generic.editable import XEditable as Editable

ELF_MAGIC = 0x464c457f


class SectionHeader(Editable):
    TYPE_PROGBITS = 1
    TYPE_SYMTAB = 2
    TYPE_STRTAB = 3
    FLAG_ALLOC = 2  # Memory section
    FLAG_EXECINSTR = 4  # Executable section

    def define(self, name):
        self.namestring = name
        self.uint32('namepos')
        self.uint32('type_')
        self.uint32('flags')
        self.uint32('address')
        self.uint32('offset')
        self.uint32('size_')
        self.uint32('link')
        self.uint32('info')
        self.uint32('align')
        self.uint32('entsize')


class Section(object):
    def __init__(self, name, type=0):
        self.header = SectionHeader(name)
        self.data = BinaryIO()
        self.header.type_ = type
        if type == SectionHeader.TYPE_STRTAB:
            self.data.writeUInt8(0)
        elif type == SectionHeader.TYPE_SYMTAB:
            self.header.entsize = Symbol(None).size()


class Symbol(Editable):
    BIND_LOCAL = 0
    BIND_GLOBAL = 1
    BIND_WEAK = 2
    TYPE_OBJECT = 1
    TYPE_FUNC = 2
    TYPE_SECTION = 3
    TYPE_FILE = 4

    def define(self, name):
        self.namestring = name
        self.uint32('namepos')
        self.uint32('value')
        self.uint32('size_')
        self.uint8('info')
        self.uint8('other')
        self.uint16('shndx')

    @property
    def bind(self):
        return self.info >> 4

    @bind.setter
    def bind(self, value):
        self.info = (self.info & 0xF) | (value << 4)

    @property
    def type_(self):
        return self.info & 0xF

    @type_.setter
    def type_(self, value):
        self.info = (self.info & 0xF0) | (value & 0xF)


class ELF(object):
    """

    Attributes
    ----------
    binary : io instance
        The main binary
    symbols : list
        List of (name, offset, type) symbols to be added
    """
    def __init__(self):
        self.symbols = []
        self.entry = 0x02000000
        self.sections = [Section(None)]
        self.shstrtab = Section('.shstrtab', SectionHeader.TYPE_STRTAB)
        self.strtab = Section('.strtab', SectionHeader.TYPE_STRTAB)
        self.symtab = Section('.symtab', SectionHeader.TYPE_SYMTAB)
        self.symtab.header.link = 2
        self.add_section(self.shstrtab)
        self.add_section(self.strtab)
        self.add_section(self.symtab)
        undef = self.add_symbol(None)
        undef.info = 0
        undef.shndx = 0

    def to_file(self, handle):
        writer = BinaryIO.adapter(handle)
        writer.writeUInt32(ELF_MAGIC)
        writer.writeUInt8(1)  # 32 bit
        writer.writeUInt8(1)  # little endian
        writer.writeUInt8(1)  # version
        writer.writeUInt8(0)  # ABI (None set)
        writer.writeUInt8(0)  # ABI (None set)
        writer.writePadding(0x10, chr(0))  # Padding - 7 bytes
        writer.writeUInt16(2)  # Executable?
        writer.writeUInt16(0x28)  # ARM architecture
        writer.writeUInt32(1)  # version
        writer.writeUInt32(self.entry)
        writer.writeUInt32(0)  # phoff?
        shoff_ofs = writer.tell()
        writer.writeUInt32(0)  # section header offset
        writer.writeUInt32(0)  # flags
        writer.writeUInt16(0x34)  # header size
        writer.writeUInt16(0)  # phentsize?
        writer.writeUInt16(0)  # phnum?
        writer.writeUInt16(self.sections[0].header.size())  # shentsize
        writer.writeUInt16(len(self.sections))  # shnum
        writer.writeUInt16(1)  # shstrndx
        for section in self.sections:
            with section.data.seek(0):
                section.header.offset = writer.tell()
                writer.write(section.data.read())
                section.header.size_ = section.data.tell()
                writer.writeAlign(4)
        shoff = writer.tell()
        with writer.seek(shoff_ofs):
            writer.writeUInt32(shoff)
        for section in self.sections:
            writer = section.header.save(writer)
        # self.binary.seek(0)
        # writer.write(self.binary.read())

    def add_section(self, section):
        self.sections.append(section)
        if section.header.namestring:
            section.header.namepos = self.shstrtab.data.tell()
            self.shstrtab.data.writeString(section.header.namestring)

    def add_binary(self, handle, name='.text', address=0x02000000):
        section = Section(name, SectionHeader.TYPE_PROGBITS)
        reader = BinaryIO.reader(handle)
        with reader.seek(0):
            section.data.write(reader.read())
        section.header.address = address
        section.header.flags = section.header.FLAG_EXECINSTR \
            | section.header.FLAG_ALLOC
        self.add_section(section)
        symbol = self.add_symbol(name, address, Symbol.TYPE_SECTION)
        symbol.type_ = symbol.TYPE_SECTION

    def add_symbol(self, name, address=0x0, type=Symbol.TYPE_OBJECT):
        symbol = Symbol(name)
        symbol.bind = symbol.BIND_GLOBAL
        symbol.type_ = type
        symbol.value = address
        symbol.shndx = 0xfff1
        if name:
            symbol.namepos = self.strtab.data.tell()
            self.strtab.data.writeString(name)
        self.symbols.append(symbol)
        self.symtab.data.write(symbol.save().getvalue())
        self.symtab.data.writeAlign(4)
        return symbol
