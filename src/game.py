import src.player as player
import src.map as map

class State(object):
    def __init__(self, map_width: int, map_height: int):
        super().__init__()
        self.map = map.Map(map.level_layout)
        # self.player = player.Player(7, 8)
        self.player = player.Player(13, 8)

    def move_player(self, direction: str) -> tuple[bool, str | None]:
        new_x, new_y = self.player.x, self.player.y

        self.player.direction = direction
        if direction == "l":
            new_x -= 1
        elif direction == "r":
            new_x += 1
        elif direction == "u":
            new_y -= 1
        elif direction == "d":
            new_y += 1

        if new_x < 0 or new_y < 0 or new_x >= self.map.width or new_y > self.map.height:
            return False, None

        the_tile = self.map.tiles[new_y][new_x]

        if self.player.selected_item is not None:
            item = self.player.items[self.player.selected_item]
            ok, msg = the_tile.on_use_with(new_x, new_y, self.player, item)
            if ok:
                self.player.selected_item = None
            return ok, msg
        else:
            return the_tile.on_use_empty(new_x, new_y, self.player)

    def summon_item(self, item: str) -> bool:
        return self.player.pickup_item(item.lower())
