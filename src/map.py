import random
import src.tile as tile

level_layout = """\
____________________________________
____________________________________
____________________________________
____7333335_________________________
____2#####4_____________73333335____
____2#B..#47333333333333a######4____
____2#.?.#ba##############!..C#4____
____2#...####..........~......#4____
____2#.!./.....!,,,?...§......#4____
____2#...####..,,+,,..####!..!#4____
____2#####dc#..,,,,,..#dc######4____
____81111162#..?,,,!.B#481111116____
___________2#.........#4____________
___________2######.####4____________
___7333335_81111c#;#d116____________
___2#####4___733a#.#b335____________
___2#,,,#4___2####.####4____________
___2#,?,#b333a#?'''''!#4____________
___2#,,,#######'''-B''#4____________
___2#R!,...I...!'''''?#4____________
___2#,,,#############.#4____________
___2#,?,#d111111111c#:#4____________
___2#,,,#4_________2#.#b333335______
___2#####4_________2#.#######4______
___8111116_________2#,,,,,,,#4______
___________________2#,?,A,!,#4______
___________________2#,,,,,,,#4______
___________________2#########4______
___________________81111111116______
____________________________________
____________________________________
____________________________________\
"""


class Map:
    TILE_MAPPING = {
        "#": tile.Wall,
        "a": tile.Border, "b": tile.Border, "c": tile.Border, "d": tile.Border,
        "1": tile.Border, "2": tile.Border, "3": tile.Border, "4": tile.Border,
        "5": tile.Border, "6": tile.Border, "7": tile.Border, "8": tile.Border,
        "~": tile.SnakePitObstacle,
        "§": tile.SnakePitObstacle,
        "I": tile.IceWallObstacle,
        "/": tile.LockedDoorObstacle,
        ";": tile.SadGuyObstacle,
        ":": tile.GreenGuyObstacle,
        "B": tile.Bin,
        "+": tile.UpgradeMachine,
        "-": tile.DowngradeMachine,
        "R": tile.RhymeMachine,
        "C": tile.CombineMachine,
        "A": tile.Floor, #tile.AntiMachine,
        "_": tile.Void,
    }

    FLOOR_TILES = {".": "default", ",": "diamond", "'": "checker", "!": "omega", "?": "lambda"}
    BORDER_TILES = {
        "1": "e1", "2": "e2", "3": "e3", "4": "e4",
        "a": "n1", "b": "n2", "c": "n3", "d": "n4",
        "5": "c1", "6": "c2", "7": "c3", "8": "c4",
    }
    SNAKE_TILES = {"~": "top", "§": "bottom"}

    def __init__(self, level_layout_str: str):
        level_layout = level_layout_str.split("\n")
        self.width = len(level_layout[0])
        self.height = len(level_layout)

        self.tiles = [
            [self.create_tile(char) for char in row]
            for row in level_layout
        ]

    def create_tile(self, char):
        if char in self.FLOOR_TILES:
            return tile.Floor(self.FLOOR_TILES[char])

        if char in self.BORDER_TILES:
            return tile.Border(self.BORDER_TILES[char])

        if char in self.SNAKE_TILES:
            return tile.SnakePitObstacle(self.SNAKE_TILES[char])

        return self.TILE_MAPPING.get(char, tile.Floor)()
