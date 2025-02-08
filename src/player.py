class Player(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def img_src(self) -> str:
        return "/static/img/player.png"

    def move(self, direction: str) -> bool:
        new_x, new_y = self.x, self.y

        if direction == "l":
            new_x -= 1
        elif direction == "r":
            new_x += 1
        elif direction == "u":
            new_y -= 1
        elif direction == "d":
            new_y += 1

        self.x, self.y = new_x, new_y

        return True
