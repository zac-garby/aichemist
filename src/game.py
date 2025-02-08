import src.map as map

class State(object):
    def __init__(self, map_width: int, map_height: int):
        super().__init__()
        self.map = map.Map(map_width, map_height)
        self.player_x = 1
        self.player_y = 1
