
from cartopy.io.img_tiles import _merge_tiles

class TileFactory(object):
    """ Implements a cartopy image "factory" than can be passed to
    GeoAxes.add_image """

    def __init__(self, tileset):
        self.tiles =[(t, _x_from_bbox(t, bb), _y_from_bbox(t, bb),
                      _origin_from_bbox(bb))
                     for t, bb in zip(tileset.tiles, tileset.bboxes)]
        raise NotImplementedError()

    def image_for_domain(self, target_domain, _):
        """ Implements method used by cartopy for drawing tile sets. The third
        argument *target_z* is ignored, because it's defined by the zoom level
        of the tileset. """
        img, extent, origin = _merge_tiles(self.tiles)
        return img, extent, origin

def _x_from_bbox(tile, bbox):
    return np.linspace(bbox[0], bbox[1], tile.shape[1])

def _y_from_bbox(tile, bbox):
    return np.linspace(bbox[2], bbox[3], tile.shape[0])

def _origin_from_bbox(bbox):
    return (bbox[0], bbox[2])
