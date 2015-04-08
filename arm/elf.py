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
    FLAG_EXECINSTR = 3  # Executable section

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
        self.strtab = Section('.shstrtab', SectionHeader.TYPE_STRTAB)
        self.add_section(self.strtab)

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
            section.header.namepos = self.strtab.data.tell()
            self.strtab.data.writeString(section.header.namestring)

    def add_binary(self, handle, name='.text', address=0x02000000):
        section = Section(name, SectionHeader.TYPE_PROGBITS)
        reader = BinaryIO.reader(handle)
        with reader.seek(0):
            section.data.write(reader.read())
        section.header.address = address
        section.header.flags = section.header.FLAG_EXECINSTR \
            | section.header.FLAG_ALLOC
        self.add_section(section)
