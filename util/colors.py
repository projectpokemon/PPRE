
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


def rotate_color(color, degrees=180):
    """Rotates the hue of an RGB color

    Parameters
    ----------
    color : RGB[A] tuple
        Color to transform
    degrees : int
        Amount to change color by. Out of 360.

    Returns
    -------
    color : RGB[A] tuple
        Rotated color
    """
    alpha = color[3:]
    hsv = colorsys.rgb_to_hsv(*(c/255.0 for c in color[:3]))
    hue = (hsv[0]*360+degrees) % 360
    color = colorsys.hsv_to_rgb(hue/360.0, hsv[1], hsv[2])
    return (int(color[0]*255), int(color[1]*255), int(color[2]*255))\
        + tuple(alpha)
