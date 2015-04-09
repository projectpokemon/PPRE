
import array
import itertools
import os
import shutil
import struct

from ntr.overlay import OverlayTable
from util.io import BinaryIO

ARM9_BLZ_BEACON = 0xdec00621
ARM9_BLZ_UNBEACON = 0x2106c0de


def decompress(reader, end):
    """BLZ Decompression taken from HGSS

    There are no differences between this and DP and BW (other than some
    bad optimization issues in BW. *cough* r8 *cough*). And yes, DP does
    have LZ compression that it does not make use in arm9.bin

    Parameters
    ----------
    reader : io instance
    end : int
        Position to start decompressing at

    Returns
    -------
    buff : array
        The fully decompressed file
    """
    reader.seek(0)
    buff = array.array('B', reader.read(end))
    reader.seek(end-8)
    topinfo = reader.readUInt32()
    diff = reader.readUInt32()
    buff.extend(itertools.repeat(0, diff))
    stop = end-(topinfo & 0xFFFFFF)
    cur = end+diff
    ptr = end-(topinfo >> 24)
    while(ptr > stop):
        ptr -= 1
        control = buff[ptr]
        shift = 8
        while shift > 0:
            shift -= 1
            if control & 0x80:
                ptr -= 1
                count = buff[ptr]
                ptr -= 1
                ofs = buff[ptr]
                ofs |= count << 8
                ofs &= 0xFFF
                ofs += 2
                count += 32  # one extra loop
                while count >= 0:
                    dup = buff[cur+ofs]
                    cur -= 1
                    buff[cur] = dup
                    count -= 16
            else:
                ptr -= 1
                cur -= 1
                dup = buff[ptr]
                buff[cur] = dup
            control <<= 1
            if ptr <= stop:
                break
    return buff


def decompress_arm9(game):
    """Creates an arm9.dec.bin in the Game's workspace

    This file will be created even if arm9.bin is already decompressed
    """
    workspace = game.files.directory
    try:
        if os.path.getsize(os.path.join(workspace, 'arm9.dec.bin')) > 0:
            return
    except OSError:
        pass
    with open(os.path.join(workspace, 'header.bin')) as header:
        header.seek(0x24)
        entry, ram_offset, size = struct.unpack('III', header.read(12))

    with open(os.path.join(workspace, 'arm9.bin')) as arm9,\
            open(os.path.join(workspace, 'arm9.dec.bin'), 'w') as arm9dec:
        arm9.seek(game.load_info-ram_offset+0x14)
        end, u18, beacon, unbeacon = struct.unpack('IIII', arm9.read(16))
        assert beacon == ARM9_BLZ_BEACON
        assert unbeacon == ARM9_BLZ_UNBEACON
        # TODO: if beacons do not match, scan ARM9 for beacon
        try:
            assert end
            arm9.seek(end-ram_offset)
            assert struct.unpack('I', arm9.read(4))[0] == ARM9_BLZ_BEACON
        except AssertionError:
            # already decompressed
            arm9.seek(0)
            arm9dec.write(arm9.read())
            return
        except struct.error:
            pass  # at EOF
        reader = BinaryIO.reader(arm9)
        buff = decompress(reader, end-ram_offset)
        for i in range(game.load_info-ram_offset+0x14,
                       game.load_info-ram_offset+0x18):
            buff[i] = 0
        buff.tofile(arm9dec)


def decompress_overlays(game):
    """Creates an overarm9.dec.bin in the Game's workspace and
    an overlays_dez directory
    """
    workspace = game.files.directory
    try:
        if os.path.getsize(os.path.join(workspace, 'overarm9.dec.bin')) > 0:
            return
    except OSError:
        pass
    try:
        os.mkdir(os.path.join(workspace, 'overlays_dez'))
    except:
        pass
    with open(os.path.join(workspace, 'header.bin')) as header:
        header.seek(0x54)
        size, = struct.unpack('I', header.read(4))
    with open(os.path.join(workspace, 'overarm9.bin')) as overarm:
        ovt = OverlayTable(size >> 5, reader=overarm)

        for overlay in ovt.overlays:
            fname = os.path.join(workspace, 'overlays',
                                 'overlay_{0:04}.bin'.format(overlay.file_id))
            outname = os.path.join(workspace, 'overlays_dez',
                                   'overlay_{0:04}.bin'.format(
                                       overlay.file_id))
            if overlay.compressed:
                end = overlay.reserved & 0xFFFFFF
                with open(fname) as compressed_handle,\
                        open(outname, 'w') as decompressed_handle:
                    reader = BinaryIO.reader(compressed_handle)
                    buff = decompress(reader, end)
                    buff.tofile(decompressed_handle)
                overlay.reserved = 0
            else:
                shutil.copy2(fname, outname)
    with open(os.path.join(workspace, 'overarm9.dec.bin'), 'w') as overarm:
        ovt.save(overarm)


if __name__ == '__main__':
    import sys

    from pokemon.game import Game

    game = Game.from_workspace(sys.argv[1])
    decompress_arm9(game)
    decompress_overlays(game)
