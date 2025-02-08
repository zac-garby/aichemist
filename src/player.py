class Player(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def img_src(self) -> str:
        return "/static/img/player.png"
