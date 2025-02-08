import src.player as player
import src.map as map

class State(object):
    def __init__(self, map_width: int, map_height: int):
        super().__init__()
        self.map = map.Map(map_width, map_height)
        self.player = player.Player(int(map_width / 2), int(map_height / 2))
