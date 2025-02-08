import src.player as player
import src.map as map

class State(object):
    def __init__(self, map_width: int, map_height: int):
        super().__init__()
        self.map = map.Map(map_width, map_height)
        self.player = player.Player(int(map_width / 2), int(map_height / 2))

    def move_player(self, direction: str) -> bool:
        new_x, new_y = self.player.x, self.player.y

        if direction == "l":
            new_x -= 1
        elif direction == "r":
            new_x += 1
        elif direction == "u":
            new_y -= 1
        elif direction == "d":
            new_y += 1

        if new_x < 0 or new_y < 0 or new_x >= self.map.width or new_y > self.map.height:
            return False

        new_tile = self.map.tiles[new_y][new_x]
        if not new_tile.passable:
            return False

        self.player.x, self.player.y = new_x, new_y

        return True
