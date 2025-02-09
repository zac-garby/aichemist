import src.player as player
import src.llm as llm

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
    def __init__(self, style: str = "default"):
        super().__init__()
        self.passable = True
        self.style = style

    def img_src(self) -> str:
        return f"/static/img/tiles/floor_{self.style}.png"

    def on_use_with(
        self, my_x: int, my_y: int, p: player.Player, item: str
    ) -> tuple[bool, str | None]:
        self.on_use_empty(my_x, my_y, p)
        return True, None

class Border(Tile):
    def __init__(self, style: str = "default"):
        super().__init__()
        self.passable = False
        self.style = style

    def img_src(self) -> str:
        return f"/static/img/tiles/{self.style}.png"

class Wall(Tile):
    def img_src(self) -> str:
        return "/static/img/tiles/bricks.png"

class Void(Tile):
    def img_src(self) -> str:
        return "/static/img/tiles/void.png"

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
        return True, f"Ding! Your {item} becomes a shiny new {output}"

    def run_machine(self, object: str) -> str:
        new_msgs = self.prime_msgs + [{
            "role": "user", "content": object
        }]

        resp = llm.chat(
            messages=new_msgs,
            schema=self.schema
        )

        if (content := resp.message.content) is not None:
            return json.loads(content)["new_object"]

        print("warning: for some reason, we couldn't get the llm output")
        return object

class Obstacle(Tile):
    def __init__(
        self,
        system_prompt: str, examples: list[tuple[str, bool, str]],
        empty_msg: str
    ):
        self.empty_msg = empty_msg
        self.cleared = False

        self.schema = {
            "title": "Obstacle result",
            "description": "A structured response about the output and reasoning of an obstacle clearance attempt.",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "description": {"type": "string"},
            },
            "required": ["success", "description"]
        }

        self.prime_msgs = [{ "role": "system", "content": system_prompt }]
        for i, succ, desc in examples:
            self.prime_msgs.append({ "role": "user", "content": i })
            self.prime_msgs.append({
                "role": "assistant",
                "content": json.dumps({
                    "success": succ, "description": desc,
                })
            })

        super().__init__()

    def on_use_empty(
        self, my_x: int, my_y: int, p: player.Player
    ) -> tuple[bool, str | None]:
        if not self.cleared:
            return False, self.empty_msg
        return super().on_use_empty(my_x, my_y, p)

    def on_use_with(
        self, my_x: int, my_y: int, p: player.Player, item: str
    ) -> tuple[bool, str | None]:
        if not self.cleared:
            succ, desc = self.run_machine(item)
            if succ:
                self.on_clear(my_x, my_y, p)

            return succ, desc

        return super().on_use_empty(my_x, my_y, p)

    def run_machine(self, object: str) -> tuple[bool, str]:
        new_msgs = self.prime_msgs + [
            {
                "role": "system",
                "content": "The previous examples were independent. Now, this\
                obstacle has its memory erased, and the following object is\
                the actual one which the player is trying. Do not mention any\
                of the previous examples again, they are just examples to explain\
                to you what to do. The player is different now."
            },
            {
                "role": "user", "content": object
            }
        ]

        resp = llm.chat(
            messages=new_msgs,
            schema=self.schema
        )

        if (content := resp.message.content) is not None:
            data = json.loads(content)
            return data["success"], data["description"]

        print("warning: for some reason, we couldn't get the llm output")
        return (False, "Something went wrong.")

    def on_clear(self, my_x: int, my_y: int, p: player.Player):
        self.cleared = True
        self.passable = True

class UpgradeMachine(Machine):
    def __init__(self):
        super().__init__(llm.upgrade_machine_prompt, [
            ("butter knife", "machete"),
            ("rock", "slingshot"),
            ("bucket", "waterproof backpack"),
            ("key", "master key"),
            ("bicycle", "motorcycle"),
        ], "Hey, it looks like this machine can upgrade my items into shiny new ones!")

    def img_src(self) -> str:
        return "/static/img/tiles/upgrade.png"

class DowngradeMachine(Machine):
    def __init__(self):
        super().__init__(llm.downgrade_machine_prompt, [
                ("chainsaw", "handsaw"),
                ("jetpack", "parachute"),
                ("laptop", "typewriter"),
                ("diamond", "glass shard"),
                ("master key", "rusty key"),
            ], "Hm. I think this machine will make my items worse?")

    def img_src(self) -> str:
        return "/static/img/tiles/downgrade.png"

class SadGuyObstacle(Obstacle):
    def __init__(self):
        super().__init__(llm.sad_guy_prompt, [
            ("teddy bear", True, "You offer the teddy bear. The little guy hugs it, sniffles, and shuffles aside with a tiny smile."),
            ("knife", True, "You brandish the knife. He flees in tears, leaving a sad puddle where he stood. You feel like a monster."),
            ("book", False, "You read him a chapter on existential philosophy. He sobs louder and curls into a ball."),
            ("chocolate bar", True, "You share the chocolate. His mood lifts instantly, and he hums a tune while letting you pass.")
        ], "There's a sad little guy here. You want to turn a blind eye, but he's blocking the way...")

    def img_src(self) -> str:
        if self.cleared:
            return "/static/img/tiles/floor_lambda.png"
        else:
            return "/static/img/tiles/sadguy.png"

class GreenGuyObstacle(Obstacle):
    def __init__(self):
        super().__init__(llm.green_guy_prompt, [
            ("trash bag", True, "You hand him a trash bag and promise to help clean up. He beams and waves you forward."),
            ("hiking boots", True, "You show off your sturdy hiking boots, ready to explore the great outdoors. He nods in approval and lets you pass."),
            ("plastic straw", False, "You offer a plastic straw. He gasps in horror and lectures you for an hour on ocean pollution."),
            ("flower seeds", True, "You present a packet of flower seeds. He claps excitedly and steps aside, eager to see them bloom."),
            ("video game console", False, "You try to impress him with a new console. He frowns and blocks your way, muttering about screen addiction."),
            ("rubber chicken", False, "You squeeze the rubber chicken. It squawks. He blinks, unimpressed, and remains firmly in place."),
            ("reusable water bottle", True, "You hand him a reusable water bottle. He nods approvingly and waves you through."),
        ], "A green-skinned guy stands in your path, passionately urging people to connect with nature. He won’t let you pass unless you prove your commitment to the environment.")

    def img_src(self) -> str:
        if self.cleared:
            return "/static/img/tiles/floor_checker.png"
        else:
            return "/static/img/tiles/greenguy.png"

class IceWallObstacle(Obstacle):
    def __init__(self):
        super().__init__(llm.ice_wall_prompt, [
            ("blowtorch", True, "You blast the ice wall with the blowtorch, carving a steamy tunnel through it in minutes."),
            ("pickaxe", True, "You chip away at the ice wall relentlessly, reducing it to a pile of slush."),
            ("book", False, "You read passages about tropical beaches to the ice wall. It remains unimpressed."),
            ("bucket of water", False, "You pour water on the ice wall, accidentally creating a slick hazard. Oops."),
        ], "Shucks, a wall of ice! How oh how will I get through such a grand obstacle?")

    def img_src(self) -> str:
        if self.cleared:
            return "/static/img/tiles/floor_1.png"
        else:
            return "/static/img/tiles/icewall.png"

class LockedDoorObstacle(Obstacle):
    def __init__(self):
        super().__init__(llm.locked_door_prompt, [
            ("key", True, "The key clicks smoothly in the lock, and the door swings open with a satisfying creak."),
            ("crowbar", True, "You wedge the crowbar into the doorframe, leveraging it open with a splintering crack."),
            ("credit card", True, "You slide the card expertly between the latch and frame, popping the door open."),
            ("banana", False, "You smush the banana into the keyhole. It’s now a locked door with a fruity secret."),
            ("frying pan", False, "You bang the pan against the door like a dinner gong. The lock remains unfazed."),
        ], "Devastatingly, this door is locked tight.")

    def img_src(self) -> str:
        if self.cleared:
            return "/static/img/tiles/open_door.png"
        else:
            return "/static/img/tiles/closed_door.png"

class SnakePitObstacle(Obstacle):
    def __init__(self, variant: str = "top"):
        self.variant = variant

        super().__init__(llm.snake_pit_prompt, [
             ("plank", True, "You balance the plank across the pit, ignoring the hissing snakes below as you sprint to safety."),
             ("flute", False, "You charm the snakes into a dance, but the pit remains uncrossed. At least the snakes are having fun."),
             ("grappling hook", True, "You launch the hook overhead, swing across the pit, and kick off a snake mid-air for style points."),
             ("balloon", True, "You inflate the balloon, float gently over the pit, and drop a snack to distract the snakes."),
             ("torch", False, "You light the torch to scare off the snakes, but the pit is still too wide to cross."),
             ("rope", True, "You throw the rope across, climb up, and safely cross over the pit, keeping your distance from the snakes."),
             ("banana peel", False, "You toss the banana peel, expecting it to act as a teleporter, but nothing happens. The snakes remain unimpressed."),
         ], "A wide pit filled with hissing snakes, but surely there’s a way across!")


    def img_src(self) -> str:
        return f"/static/img/tiles/snakes_{self.variant}.png"

    def on_clear(self, my_x: int, my_y: int, p: player.Player):
        dx, dy = my_x - p.x, my_y - p.y
        p.x = my_x + dx
        p.y = my_y + dy
