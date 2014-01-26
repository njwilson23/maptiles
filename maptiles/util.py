
from PIL import Image

def composetiles(tiles, XY):
    """ From a list of equalliy-sized map tiles and tile coordinates (starting
    from 0), construct a mosaic. """
    tx, ty = tiles[0].size
    xs = [xy[0] for xy in XY]
    ys = [xy[1] for xy in XY]
    nx = max(xs) - min(xs) + 1
    ny = max(ys) - min(ys) + 1
    bigtile = Image.new("RGB", (nx*tx, ny*ty), (0,0,0))
    for tile, xy in zip(tiles, XY):
        bigtile.paste(tile, (xy[0]*tx, xy[1]*ty))
    return bigtile


