class Player(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.items: list[str] = [
            "Watermelon",
            "Water Balloon"
        ]
        self.selected_item: int | None = None

    def img_src(self) -> str:
        return "/static/img/player.png"

    def select_item(self, index: int) -> bool:
        if index >= len(self.items) or index == self.selected_item:
            self.selected_item = None
        else:
            self.selected_item = index

        return True
