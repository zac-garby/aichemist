import random
import src.tile as tile

class Map(object):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(random.choice([tile.Floor(), tile.Wall()]))
            self.tiles.append(row)
