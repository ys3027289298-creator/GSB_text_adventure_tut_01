__author__ = 'Phillip Johnson'

_world = {}
starting_position = (0, 0)

def tile_exists(x, y):
        """Returns the tile at the given coordinates or None if there is no tile.

        :param x: the x-coordinate in the worldspace
        :param y: the y-coordinate in the worldspace
        :return: the tile at the given coordinates or None if there is no tile
        """
        return _world.get((x, y))


def load_tiles(map_file='resources/map.txt'):
    """Parses a file that describes the world space into the _world object"""
    global _world, starting_position
    _world = {}
    with open(map_file, 'r') as f:
        rows = f.readlines()
    for y in range(len(rows)):
        cols = rows[y].split('\t')
        for x in range(len(cols)):
            tile_name = cols[x].strip()
            if tile_name == 'StartingRoom':
                starting_position = (x, y)
            _world[(x, y)] = None if tile_name == '' else getattr(__import__('tiles'), tile_name)(x, y)

