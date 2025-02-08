import src.player as player

import json

class Tile(object):
    def __init__(self):
        self.passable = False

    def img_src(self) -> str:
        raise NotImplementedError()

    def on_use_empty(
        self, my_x: int, my_y: int, p: player.Player
    ) -> tuple[bool, str | None]:
        if not self.passable:
            return False, "You can't walk through that!"

        p.x, p.y = my_x, my_y
        return True, None

# tile definitions:

class Floor(Tile):
    def __init__(self):
        super().__init__()
        self.passable = True

    def img_src(self) -> str:
        return "/static/img/tiles/floor.png"

class Wall(Tile):
    def img_src(self) -> str:
        return "/static/img/tiles/wall.png"
