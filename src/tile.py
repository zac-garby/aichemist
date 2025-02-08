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
            return False, f"You can't walk through that {self.__class__.__name__}!"

        p.x, p.y = my_x, my_y
        return True, None

    def on_use_with(
        self, my_x: int, my_y: int, p: player.Player, item: str
    ) -> tuple[bool, str | None]:
        return False, f"You can't use the {item} on the {self.__class__.__name__}!"

# tile definitions:

class Floor(Tile):
    def __init__(self):
        super().__init__()
        self.passable = True

    def img_src(self) -> str:
        return "/static/img/tiles/floor.png"

    def on_use_with(
        self, my_x: int, my_y: int, p: player.Player, item: str
    ) -> tuple[bool, str | None]:
        return True, None

class Wall(Tile):
    def img_src(self) -> str:
        return "/static/img/tiles/wall.png"
