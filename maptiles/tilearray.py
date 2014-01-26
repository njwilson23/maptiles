""" Module to get mappig tiles from a tile server (e.g. MapQuest,
OpenStreetMaps, Google Maps. """

import os
import math
from math import pi, floor
import urllib2
import cStringIO
from PIL import Image
import util

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
        if not isinstance(key, tuple):
            raise NotImplementedError()

        if isinstance(key[0], slice) and isinstance(key[1], slice):
            assert(len(key) == 2)

            nw = self._getxy((key[0].start, key[1].stop), self.default_zoom)
            se = self._getxy((key[0].stop, key[1].start), self.default_zoom)
            tiletuples = [(x,y) for x in xrange(nw[0], se[0]+1)
                                for y in xrange(nw[1], se[1]+1)]
            if len(tiletuples) > 9:
                raise Exception("too many tiles ({0}) - choose a lower zoom "
                                "level".format(len(tiletuples)))
            tiles = []
            bigxy = []
            for tt in tiletuples:
                addr = self.construct_addr(self.default_zoom, tt[0], tt[1])
                tile = self.download_tile(addr)
                tiles.append(tile)
                bigxy.append((tt[0] - nw[0], tt[1] - nw[1]))
            bigtile = util.composetiles(tiles, bigxy)
            return bigtile

        else:
            tiletuple = self.get_tile_addr((key[0], key[1]), self.default_zoom)
            addr = self.construct_addr(*tiletuple)
            tile = self.download_tile(addr)
            return tile

    def _getxy(self, coords, zoom):
        n = 2**zoom
        lat = coords[1] * pi / 180.0
        lon = coords[0] * pi / 180.0
        yp = math.asinh(math.tan(lat))
        x = int(floor((1 + (lon / pi)) / 2 * n))
        y = int(floor((1 - (yp / pi)) / 2 * n))
        return x, y

    def get_bbox(self, X, Y, zoom=None):
        """ Get the coordinate bounding box spanned by a range given by tuples
        as (lonmin, lonmax), (latmin, latmax). """
        if zoom is None:
            zoom = self.default_zoom
        nwextents = self.get_extents((X[0], Y[1]), zoom)
        seextents = self.get_extents((X[1], Y[0]), zoom)
        bbox = (nwextents[0], seextents[1], seextents[2], nwextents[3])
        return bbox

    def get_extents(self, coords, zoom=None):
        """ Return the spatial extents of a tile containing *coordinates* at
        zoom level *zoom*.
        """
        if zoom is None:
            zoom = self.default_zoom
        x, y = self._getxy(coords, zoom)
        n = 2**zoom
        minx = 360.0 / n * x - 180
        maxx = 360.0 / n * (x+1) - 180
        miny = pi * (1 - 2.0*(y+1)/n)
        maxy = pi * (1 - 2.0*y/n)
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

