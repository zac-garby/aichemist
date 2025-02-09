import ollama
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
            return False, None

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
        self.on_use_empty(my_x, my_y, p)
        return True, None

class Wall(Tile):
    def img_src(self) -> str:
        return "/static/img/tiles/wall.png"

class Machine(Tile):
    def __init__(
        self,
        system_prompt: str, examples: list[tuple[str, str]],
        empty_msg: str
    ):
        self.empty_msg = empty_msg

        self.schema = {
            "title": "Machine result",
            "description": "A structured response about the output of a machine which transforms objects.",
            "type": "object",
            "properties": {
                "new_object": {"type": "string"}
            },
            "required": "new_object"
        }

        self.prime_msgs = [{ "role": "system", "content": system_prompt }]
        for i, o in examples:
            self.prime_msgs.append({ "role": "user", "content": i })
            self.prime_msgs.append({
                "role": "assistant", "content": f'{{"new_object": "{o}"}}'
            })

        super().__init__()

    def on_use_empty(
        self, my_x: int, my_y: int, p: player.Player
    ) -> tuple[bool, str | None]:
        return False, self.empty_msg

    def on_use_with(
        self, my_x: int, my_y: int, p: player.Player, item: str
    ) -> tuple[bool, str | None]:
        output = self.run_machine(item)
        p.replace_item(output)
        return True, f"Ding! Your {item} has been upgraded to a shiny new {output}"

    def run_machine(self, object: str) -> str:
        new_msgs = self.prime_msgs + [{
            "role": "user", "content": object
        }]

        resp = ollama.chat(
            model="phi4",
            messages=new_msgs,
            format=self.schema,
            options={ "seed": 42 }
        )

        if (content := resp.message.content) is not None:
            return json.loads(content)["new_object"]

        print("warning: for some reason, we couldn't get the llm output")
        return object

class UpgradeMachine(Machine):
    def __init__(self):
        super().__init__("""
        You are the logic core of an "Upgrade Machine" in a puzzle game. Players insert real-world objects, and you output an improved version of the item that is more effective, advanced, or specialized for solving challenges.

        Rules:

        Upgrade Definition:

            Functional: A more powerful tool (e.g., candle → flashlight, stick → spear).
            Material: A sturdier/durable version (e.g., wooden ladder → aluminum ladder, rope → steel cable).
            Technological: A modernized or advanced equivalent (e.g., compass → GPS, notebook → tablet).

        Output MUST be:

            A single, physical object (no abstract concepts, adjectives, or states like "stronger" or "electric").
            A direct upgrade (e.g., "penny" might go to "dime" [value], "mug" might go to "thermos" [utility]).
            No more than three words long, and only words. No symbols.
            In JSON format with one string field, "new_object".

        If no logical upgrade exists, return the original object. If the new object
        isn't strictly better, or is just a rewording, just return the original.
        If it already seems very complicated, then just
        return the same object. DO NOT keep adding adjectives for the sake of it.
        It's better to give a new noun than to add "good" adjectives to the old one.
        """, [
            ("butter knife", "machete"),
            ("rock", "slingshot"),
            ("bucket", "waterproof backpack"),
            ("key", "master key"),
            ("bicycle", "motorcycle"),
        ], "Hey, it looks like this machine can upgrade my items into shiny new ones!")

    def img_src(self) -> str:
        return "/static/img/sprite tiles/upgrade.png"
