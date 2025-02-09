class Player(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.items: list[str] = [
            "peanut",
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

    def replace_item(self, item: str):
        if self.selected_item is not None:
            self.items[self.selected_item] = item
        else:
            self.pickup_item(item)

    def pickup_item(self, item: str) -> bool:
        if len(self.items) < 4:
            self.items.append(item)
            return True
        else:
            return False

    def drop_item(self, item: str):
        for i in range(len(self.items)):
            if self.items[i] == item:
                self.items.pop(i)
                break

        self.selected_item = None
