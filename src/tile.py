import json

class Tile(object):
    def __init__(self):
        self.passable = False

    def img_src(self) -> str:
        raise NotImplementedError()

class Floor(Tile):
    def __init__(self):
        super().__init__()
        self.passable = True

    def img_src(self) -> str:
        return "/static/img/tiles/floor.png"

class Wall(Tile):
    def __init__(self):
        super().__init__()

    def img_src(self) -> str:
        return "/static/img/tiles/wall.png"
