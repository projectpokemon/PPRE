
import colorsys


def color_gen():
    """Yields unique 32-bit RGBA color tuples each iteration
    """
    chunks = 2
    while True:
        for pos in xrange(chunks):
            if pos % 2:
                color = colorsys.hsv_to_rgb(float(pos)/chunks, 1, 0.9)
                yield (int(color[0]*255), int(color[1]*255),
                       int(color[2]*255), 255)
        chunks <<= 1
