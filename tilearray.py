""" Module to get mappig tiles from a tile server (e.g. MapQuest,
OpenStreetMaps, Google Maps. """

import os
import math
from math import pi, floor
import urllib2
import cStringIO
from PIL import Image

MAXLAT = math.atan(math.sinh(math.pi)) * 180.0 / math.pi

class TileArray(object):
    """ TileArray is a class that handles getting online map tiles. Through
    __getitem__ magic, the caller gets access to tiles using geographical
    coordinates.
    """
    def __init__(self, url, default_zoom=3):
        self.url = url
        self.default_zoom = default_zoom
        return

    def __getitem__(self, key):
        pass

    def _getxy(self, coords, zoom):
        n = 2**zoom
        lat = coords[1] * pi / 180.0
        lon = coords[0] * pi / 180.0
        yp = math.asinh(math.tan(lat))
        x = int(floor((1 + (lon / pi)) / 2 * n))
        y = int(floor((1 - (yp / pi)) / 2 * n))
        return x, y

    def get_extents(self, coords, zoom):
        """ Return the spatial extents of a tile containing *coordinates* at
        zoom level *zoom*.
        """
        x, y = self._getxy(coords, zoom)
        n = 2**zoom
        minx = 360.0 / n * x - 180
        maxx = 360.0 / n * (x+1) - 180
        miny = pi * (1 - 2.0*y/n)
        maxy = pi * (1 - 2.0*(y+1)/n)
        iproj = lambda yp: math.atan(math.sinh(yp)) * 180 / pi
        return (minx, maxx, iproj(miny), iproj(maxy))

    def get_tile_addr(self, coords, zoom=None):
        """ Given a lat/lon tuple (coords), return a tuple (zoom, col, row)
        for the tile address. """
        if zoom is None:
            zoom = self.default_zoom
        if abs(coords[1]) > MAXLAT:
            raise ValueError(u"Tile servers only contain tiles to {0}\u00b0 "
                             "latitude".format(round(MAXLAT, 2)))
        x, y = self._getxy(coords, zoom)
        return (zoom, x, y)

    def construct_addr(self, zoom, col, row):
        """ From a tuple (zoom, column, row) construct a url based on the 
        tileserver at self.url. """
        addr = os.path.join(self.url, str(zoom), str(col), str(row)) + ".jpg"
        return addr

    def download_tile(self, addr):
        """ Download the tile at a provided address and return a PIL Image
        object. """
        jpg = urllib2.urlopen(addr)
        tile = Image.open(cStringIO.StringIO(jpg.read()))
        return tile

    def get_tile(self, coords, zoom=None):
        """ Return the tile corresponding to a lon-lat coordinate pair. """
        tiletuple = self.get_tile_addr(coords, zoom)
        addr = self.construct_addr(*tiletuple)
        tile = self.download_tile(addr)
        return tile

