
from collections import namedtuple
import struct

from rawdb.generic.archive import Archive
from rawdb.ntr.g3d.resdict import G3DResDict
from rawdb.util.io import BinaryIO

from PIL import Image


def log2(x):
    """Integer log2"""
    return x.bit_length()-1


class TexInfo(object):
    INFO_TEX = 0
    INFO_TEX4X4 = 1
    INFO_PAL = 2

    def __init__(self, tex, infotype=0):
        self.tex = tex
        self.vramkey = 0
        self.infotype = infotype

    def load(self, reader):
        self.vramkey = reader.readUInt32()
        self._datasize = reader.readUInt16()
        if self.infotype != TexInfo.INFO_PAL:
            self._lookupofs = reader.readUInt16()
        reader.readUInt16()  # Runtime-loaded
        if self.infotype == TexInfo.INFO_PAL:
            self._lookupofs = reader.readUInt16()
        reader.readUInt16()  # Padding, always 0x8
        self._dataofs = reader.readUInt32()
        if self.infotype == TexInfo.INFO_TEX4X4:
            self._paldataofs = reader.readUInt32()
            self._datasize <<= 2
        else:
            self._datasize <<= 3

    def save(self, writer=None):
        """
        When writing the general structure, it saves offsets
        to unknown values. It is the duty of the parent to
        fill these in
        """
        writer = writer if writer is not None else BinaryIO()
        writer.writeUInt32(self.vramkey)
        self._datasize_ofs = writer.tell()
        writer.writeUInt16(0)  # datasize
        if self.infotype != TexInfo.INFO_PAL:
            self._lookupofs_ofs = writer.tell()
            writer.writeUInt16(0)
        writer.writeUInt16(0)
        if self.infotype == TexInfo.INFO_PAL:
            self._lookupofs_ofs = writer.tell()
            writer.writeUInt16(0)
        writer.writeUInt16(8)
        self._dataofs_ofs = writer.tell()
        writer.writeUInt32(0)
        if self.infotype == TexInfo.INFO_TEX4X4:
            writer.writeUInt32(0)
        return writer


TexParam = namedtuple('TexParam', 'ofs width height format color0')
PalParam = namedtuple('PalParam', 'ofs count4')


class TEX(Archive):
    def __init__(self, reader=None):
        self.magic = 'TEX0'
        self.endian = 0xFFFE
        self.texinfo = TexInfo(self)
        self.tex4x4info = TexInfo(self, TexInfo.INFO_TEX4X4)
        self.palinfo = TexInfo(self, TexInfo.INFO_PAL)
        self.texdict = G3DResDict()
        self.texdict.sizeunit = 8
        self.paldict = G3DResDict()
        self.texparams = []
        self.palparams = []
        self.texdata = ''
        self.paldata = ''
        if reader is not None:
            self.load(reader)

    def _get_bitmaps(self):
        """List of 2d bitmaps

        Each pixel is a tuple of (index, alpha)
        """
        bitmaps = []
        for param in self.texparams:
            pixels = []  # 1d
            if param.format == 1:  # A3I5
                block = self.texdata[param.ofs:param.ofs +
                                     param.width*param.height]
                for value in block:
                    value = ord(value)
                    index = value & 0x1F
                    alpha = ((value >> 5) & 0x7)*36
                    if not index and param.color0:
                        alpha = 0
                    pixels += [(index, alpha)]
            elif param.format == 2:  # I2 4 colors
                block = self.texdata[param.ofs:param.ofs +
                                     (param.width*param.height >> 2)]
                for value in block:
                    value = ord(value)
                    for shift in xrange(0, 8, 2):
                        index = value >> shift & 0x3
                        alpha = None
                        if not index and param.color0:
                            alpha = 0
                        pixels += [(index, alpha)]
            elif param.format == 3:  # I4 16 colors
                block = self.texdata[param.ofs:param.ofs +
                                     (param.width*param.height >> 1)]
                for value in block:
                    value = ord(value)
                    for shift in xrange(0, 8, 4):
                        index = value >> shift & 0xF
                        alpha = None
                        if not index and param.color0:
                            alpha = 0
                        pixels += [(index, alpha)]
            elif param.format == 4:  # I8 256 colors
                block = self.texdata[param.ofs:param.ofs +
                                     param.width*param.height]
                for value in block:
                    index = ord(value)
                    alpha = None
                    if not index and param.color0:
                        alpha = 0
                    pixels += [(index, alpha)]
            elif param.format == 6:  # A5I3
                block = self.texdata[param.ofs:param.ofs +
                                     param.width*param.height]
                for value in block:
                    value = ord(value)
                    index = value & 0x7
                    alpha = ((value >> 3) & 0x1F)*8
                    if not index and param.color0:
                        alpha = 0
                    pixels += [(index, alpha)]
            pixels2d = [pixels[i:i+param.width]
                        for i in xrange(0, len(pixels), param.width)]
            # img = Image.frombytes('RGBA', (param.width, param.height),
            #                       data)
            bitmaps.append(pixels2d)
        return bitmaps

    def _get_palettes(self):
        palettes = []
        for param in self.palparams:
            palette = []
            data = self.paldata[param.ofs:param.ofs+512]
            values = [struct.unpack('H', data[i:i+2])[0]
                      for i in xrange(0, len(data), 2)]
            for value in values:
                palette.append(struct.pack('4B',
                                           (value >> 0 & 0x1F) << 3,
                                           (value >> 5 & 0x1F) << 3,
                                           (value >> 10 & 0x1F) << 3,
                                           255))
            palettes.append(palette)
        return palettes

    def _get_imagemap(self):
        imagemap = []
        if self.paldict.num == self.texdict.num:
            imagemap = zip(xrange(self.texdict.num),
                           xrange(self.paldict.num))
        elif self.paldict.num == 1:
            imagemap = zip(xrange(self.texdict.num),
                           [0]*self.texdict.num)
        else:  # Mtx Merger
            for texidx, texname in enumerate(self.texdict.names):
                match = 0
                best = 0
                for palidx, palname in enumerate(self.paldict.names):
                    for c in xrange(16):
                        try:
                            if palname[c] != texname[c]:
                                break
                        except:
                            break
                    if c > match:
                        match = c
                        best = palidx
                imagemap.append((texidx, best))
        return imagemap

    def _get_images(self):
        self._images = []
        bitmaps = self._get_bitmaps()
        palettes = self._get_palettes()
        for texidx, palidx in self._get_imagemap():
            palette = palettes[palidx]
            bitmap = bitmaps[texidx]
            data = ''
            for row in bitmap:
                for pix in row:
                    if pix[1] is None:
                        data += palette[pix[0]]
                    else:
                        data += palette[pix[0]][:3] + chr(pix[1])
            self._images.append(Image.frombytes('RGBA',
                                                (len(row), len(bitmap)),
                                                data))
        return self._images

    @property
    def images(self):
        """List of PIL Images
        """
        try:
            return self._images
        except AttributeError:
            return self._get_images()

    def load(self, reader):
        start = reader.tell()
        self.magic = reader.read(4)
        size = reader.readUInt32()
        self.texinfo.load(reader)
        self.tex4x4info.load(reader)
        self.palinfo.load(reader)
        # Build dicts
        reader.seek(start+self.texinfo._lookupofs)
        self.texdict.load(reader)
        self.texparams = []
        for i in xrange(self.texdict.num):
            imgParam, extra = struct.unpack('II', self.texdict.data[i])
            self.texparams.append(TexParam((imgParam & 0xFFFF) << 3,
                                           8 << ((imgParam >> 20) & 0x7),
                                           8 << ((imgParam >> 23) & 0x7),
                                           (imgParam >> 26) & 0x7,
                                           (imgParam >> 29) & 0x1))
        reader.seek(start+self.palinfo._lookupofs)
        self.paldict.load(reader)
        self.palparams = []
        for i in xrange(self.paldict.num):
            offset, flag = struct.unpack('HH', self.paldict.data[i])
            self.palparams.append(PalParam(offset << 3, flag))
        # Read data.
        reader.seek(start+self.texinfo._dataofs)
        self.texdata = reader.read(self.texinfo._datasize)
        reader.seek(start+self.palinfo._dataofs)
        self.paldata = reader.read(self.palinfo._datasize)
        # TODO 4x4
        if size:
            reader.seek(start+size)
        try:
            del self._images
        except:
            pass

    def save(self, writer=None):
        writer = writer if writer is not None else BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        size_ofs = writer.tell()
        writer.writeUInt32(0)
        writer = self.texinfo.save(writer)
        writer = self.tex4x4info.save(writer)
        writer = self.palinfo.save(writer)

        writer.writeAlign(4)
        ofs = writer.tell()-start
        with writer.seek(self.texinfo._lookupofs_ofs):
            writer.writeUInt16(ofs)
        for i in xrange(self.texdict.num):
            texparam = self.texparams[i]
            self.texdict.data[i] = \
                struct.pack('II',
                            (texparam.ofs >> 3) |
                            ((log2(texparam.width) >> 3) << 20) |
                            ((log2(texparam.height) >> 3) << 23) |
                            (texparam.format << 26) |
                            (texparam.color0 << 29), 0)
        writer = self.texdict.save(writer)

        writer.writeAlign(4)
        ofs = writer.tell()-start
        with writer.seek(self.palinfo._lookupofs_ofs):
            writer.writeUInt16(ofs)
        for i in xrange(self.texdict.num):
            param = self.palparams[i]
            self.paldict.data[i] = struct.pack('HH', param.ofs, param.count4)
        writer = self.paldict.save(writer)

        writer.writeAlign(8)
        ofs = writer.tell()-start
        with writer.seek(self.texinfo._dataofs_ofs):
            writer.writeUInt32(ofs)  # texinfo dataofs
        datastart = writer.tell()
        writer.write(self.texdata)
        writer.writeAlign(8)
        size = writer.tell()-datastart
        with writer.seek(self.texinfo._datasize_ofs):
            writer.writeUInt16(size >> 3)  # texinfo datasize

        writer.writeAlign(8)
        ofs = writer.tell()-start
        with writer.seek(self.palinfo._dataofs_ofs):
            writer.writeUInt32(ofs)  # palinfo dataofs
        datastart = writer.tell()
        writer.write(self.paldata)
        writer.writeAlign(8)
        size = writer.tell()-datastart
        with writer.seek(self.palinfo._datasize_ofs):
            writer.writeUInt16(size >> 3)  # palinfo datasize

        return writer
