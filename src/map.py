import random
import src.tile as tile

class Map(object):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.tiles: list[list[tile.Tile]] = []

        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or y == 0 or x+1 == width or y+1 == height:
                    row.append(tile.Wall())
                else:
                    row.append(tile.Floor())
            self.tiles.append(row)

        self.tiles[4][2] = tile.UpgradeMachine()
        self.tiles[4][6] = tile.DowngradeMachine()
        self.tiles[2][4] = tile.SadGuyObstacle()
        self.tiles[6][4] = tile.IceWallObstacle()
