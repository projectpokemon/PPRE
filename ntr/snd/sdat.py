"""Sound Data Archive"""

import array
from itertools import izip

from generic import Editable
from generic.archive import Archive
from generic.collection import SizedCollection
from util import BinaryIO


class SYMB(Editable):
    """SDAT Symbols

    These contain the "filenames" of the archive data.
    """
    record_names = ['SEQ', 'SEQARC', 'BANK', 'WAVEARC', 'PLAYER',
                    'GROUP', 'PLAYER2', 'STRM']

    def define(self, sdat):
        self.sdat = sdat
        self.string('magic', length=4, default='SYMB')
        self.uint32('size')
        self.array('record_offsets', self.uint32, length=14)
        self.records = {}

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        Editable.load(self, reader)
        self.records = {}
        for record_ofs, record_name in zip(self.record_offsets,
                                           self.record_names):
            if not record_ofs:
                continue
            reader.seek(start+record_ofs)
            num = reader.readUInt32()
            if record_name == 'SEQARC':
                offsets = []
                for i in range(num):
                    offsets.append((reader.readUInt32(), reader.readUInt32()))
                entries = []
                for i, (offset, sub_offset) in enumerate(offsets):
                    reader.seek(start+offset)
                    name = reader.readString()
                    reader.seek(start+sub_offset)
                    prefix = (record_name, name)
                    entries += self.load_entries(reader, start, prefix, num)
            else:
                entries = self.load_entries(reader, start, (record_name,), num)
            self.records[record_name] = entries

    @staticmethod
    def load_entries(reader, base_offset, prefix, num):
        offsets = []
        for i in range(num):
            offsets.append(reader.readUInt32())
        entries = []
        for i, offset in enumerate(offsets):
            if not offset:
                entries.append(prefix+(str(i),))
                continue
            reader.seek(base_offset+offset)
            entries.append(prefix+(reader.readString(),))
        return entries

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        for record_idx, record_name in enumerate(self.record_names):
            self.record_offsets[record_idx] = writer.tell()-start
            if record_name == 'SEQARC':
                prefixes = set()
                offsets = []
                for entry in self.records[record_name]:
                    if entry[0] == record_name:
                        prefixes.add(entry[1])
                writer.writeUInt32(len(prefixes))
                ofs_ofs = writer.tell()
                for i in range(len(prefixes)*2):
                    writer.writeUInt32(0)
                for name in prefixes:
                    offsets.append(writer.tell()-start)
                    writer.writeString(name)
                    writer.writeAlign(8)
                    offsets.append(writer.tell()-start)
                    num, text_writer = self.save_entries(
                        self.records[record_name], writer.tell()-start+4,
                        (record_name, name))
                    writer.writeUInt32(num)
                    writer.write(text_writer.getvalue())
                with writer.seek(ofs_ofs):
                    writer.write(array.array('I', offsets).tostring())
            else:
                num, text_writer = self.save_entries(
                    self.records[record_name], writer.tell()-start+4,
                    (record_name,))
                writer.writeUInt32(num)
                writer.write(text_writer.getvalue())
            writer.writeAlign(8)
        self.size = writer.tell()-start
        with writer.seek(start):
            writer = Editable.save(self, writer)
        return writer

    @staticmethod
    def save_entries(entries, base_offset, prefix):
        entry_names = []
        offsets = []
        text_writer = BinaryIO()
        for entry in entries:
            if entry[:-1] == prefix:
                entry_names.append(entry[-1])
        for i in range(len(entry_names)):
            text_writer.writeUInt32(0)
        for entry in entry_names:
            offsets.append(text_writer.tell()+base_offset)
            text_writer.writeString(entry)
        with text_writer.seek(0):
            text_writer.write(array.array('I', offsets).tostring())
        return len(entry_names), text_writer


class InfoSEQ(Editable):
    # accelerated = True

    def define(self):
        self.uint16('file_id')
        self.uint16('u2')
        self.uint16('bank_id')
        self.uint8('volume')
        self.uint8('cpr')
        self.uint8('ppr')
        self.uint8('poly')
        self.uint16('ua')


class InfoARC(Editable):
    """Info for both SEQARC and WAVEARC"""
    accelerated = True

    def define(self):
        self.uint16('file_id')
        self.uint16('u2')


class InfoBANK(Editable):
    accelerated = True

    def define(self):
        self.uint16('file_id')
        self.uint16('u2')
        self.array('wavearc_ids', self.uint16, length=4)


class InfoPLAYER(Editable):
    accelerated = True

    def define(self):
        self.uint32('u0')
        self.uint32('u4')


class InfoGROUPEntry(Editable):
    accelerated = True

    def define(self):
        self.uint32('type_')
        self.uint32('entry_id')


class InfoGROUP(Editable):
    def define(self):
        self.uint32('num')
        self.entries = []

    def load(self, reader):
        Editable.load(self, reader)
        self.entries = SizedCollection(InfoGROUPEntry().base_struct,
                                       length=self.num)


class InfoPLAYER2(Editable):
    accelerated = True

    def define(self):
        self.array('u0', self.uint8, length=24)


class InfoSTRM(Editable):
    accelerated = True

    def define(self):
        self.uint16('file_id')
        self.uint16('unknown')
        self.uint8('volume')
        self.uint8('pri')
        self.uint8('ply')
        self.uint8('u7')
        self.uint32('u8')


class INFO(Editable):
    record_classes = [InfoSEQ, InfoARC, InfoBANK, InfoARC, InfoPLAYER,
                      InfoGROUP, InfoPLAYER2, InfoSTRM]

    def define(self, sdat):
        self.sdat = sdat
        self.string('magic', length=4, default='INFO')
        self.uint32('size_')
        self.array('record_offsets', self.uint32, length=14)
        self.records = {}

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        Editable.load(self, reader)
        self.records = {}
        for i, record_ofs in enumerate(self.record_offsets):
            if not record_ofs:
                continue
            reader.seek(start+record_ofs)
            num = reader.readUInt32()
            offsets = SizedCollection(self.uint32, length=num)
            offsets.load(reader=reader)
            first_entry = expected = reader.tell()-start
            template_entry = self.record_classes[i]()
            entry_size = template_entry.get_size()
            for offset in offsets.entries:
                if offset != expected:
                    break
            else:
                entries = SizedCollection(template_entry.base_struct,
                                          length=num)
                entries.load(reader=reader)
                self.records[SYMB.record_names[i]] = entries
                continue

            adjusted_num = (max(offsets.entries[:]+[first_entry])-first_entry)/entry_size+1
            entries = SizedCollection(template_entry.base_struct,
                                      length=adjusted_num)
            entries.load(reader=reader)

            new_entries = SizedCollection(self.record_classes[i]().base_struct,
                                          length=num)
            for idx, offset in enumerate(offsets.entries):
                if not offset:  # what are these entries even?
                    new_entries[idx].file_id = 0
                    continue
                target = (offset-first_entry)/entry_size
                new_entries[idx] = entries.entries[target]
            self.records[SYMB.record_names[i]] = new_entries


class FAT(Editable):
    def define(self, sdat):
        self.sdat = sdat
        self.string('magic', length=4, default='FAT ')
        self.uint32('size_')
        self.uint32('num')
        self.entries = []

    def load(self, reader):
        Editable.load(self, reader)
        self.entries = []
        for i in range(self.num):
            start = reader.readUInt32()
            stop = start+reader.readUInt32()
            reader.read(8)
            self.entries.append(slice(start, stop))


class FILE(Editable):
    def define(self, sdat):
        self.sdat = sdat
        self.string('magic', length=4, default='FILE')
        self.uint32('size_')
        self.uint32('num')
        self.uint32('uc')
        self.files = []


class SDAT(Archive, Editable):
    """Sound Data Archive"""
    extension = ''  # filenames include their own extension

    def define(self):
        self.string('magic', length=4, default='SDAT')
        self.uint16('endian', default=0xFEFF)
        self.uint16('version', default=0x0001)
        self.uint32('size_')
        self.uint16('headersize')
        self.uint16('numblocks', default=4)
        block_ofs = Editable()
        block_ofs.uint32('block_offset')
        block_ofs.uint32('block_size')
        block_ofs.freeze()
        self.array('block_offsets', block_ofs.base_struct, length=8)
        self.symb = SYMB(self)
        self.info = INFO(self)
        self.fat = FAT(self)
        self.file = FILE(self)

    @property
    def files(self):
        files = {}
        for name in SYMB.record_names:
            try:
                self.info.records[name][0].file_id
            except:
                continue
            for name_parts, entry in izip(self.symb.records[name],
                                          self.info.records[name]):
                data = self.file.files[entry.file_id]
                files['/'.join(name_parts)+'.'+data[:4].lower()] = data
        return files

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        Editable.load(self, reader)
        assert self.magic == 'SDAT'
        for block_ofs, block in zip(self.block_offsets, [
                self.symb, self.info, self.fat, self.file]):
            if not block_ofs.block_offset:
                continue
            reader.seek(start+block_ofs.block_offset)
            block.load(reader)
        self.file.files = []
        for entry in self.fat.entries:
            reader.seek(start+entry.start)
            self.file.files.append(reader.read(entry.stop-entry.start))

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        for block_ofs, block in zip(self.block_offsets, [
                self.symb, self.fat, self.info, self.file]):
            block_ofs.block_offset = writer.tell()-start
            writer = block.save(writer)
            writer.writeAlign(4)
            block_ofs.block_size = writer.tell()-start-block_ofs.block_offset
        with writer.seek(start):
            writer = Editable.save(self, writer)
        return writer
