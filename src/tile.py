import ollama
import src.player as player

import json

llm_model: str = "llava"

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

        resp = ollama.chat(
            model=llm_model,
            messages=new_msgs,
            format=self.schema,
            options={ "seed": 42 },
            keep_alive="20m"
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

        resp = ollama.chat(
            model=llm_model,
            messages=new_msgs,
            format=self.schema,
            options={ "seed": 42 },
            keep_alive="20m"
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
        super().__init__("""
        You are the logic core of an "Upgrade Machine" in a puzzle game. Players
        insert real-world objects, and you output an improved version of the item
        that is more effective, advanced, or specialized for solving challenges.

        Rules:
        Upgrade Definition:
            Functional: A more powerful tool (e.g., candle → flashlight, stick → spear).
            Material: A sturdier/durable version (e.g., wooden ladder → aluminum ladder, rope → steel cable).
            Technological: A modernized or advanced equivalent (e.g., compass → GPS, notebook → tablet).

        Output MUST be:
            A single, physical object (no abstract concepts, adjectives, or states like "stronger" or "electric").
            A direct upgrade (e.g., "penny" might go to "dime" [value], "mug" might go to "thermos" [utility]).
            No more than three words long, and only words. No symbols. If three words,
            make them short.
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
        return "/static/img/tiles/upgrade.png"

class DowngradeMachine(Machine):
    def __init__(self):
        super().__init__("""
            You are the logic core of a "Downgrade Machine" in a puzzle game. Players insert real-world objects, and you output a worse, primitive, or broken version of the item to solve challenges in unintended ways.

            Rules:
            Downgrade Definition:
                Functional: A less effective tool (e.g., flashlight → candle, sword → stick).
                Material: A weaker/fragile version (e.g., glass cup → clay cup, steel hammer → wooden mallet).
                Technological: An older or obsolete equivalent (e.g., smartphone → rotary phone, GPS → compass).
                Broken/Flawed: A damaged or incomplete version (e.g., bucket → bucket with holes, motorcycle → bicycle).

            Output MUST be:
                A single, physical object (no abstract concepts, adjectives, or states like "stronger" or "electric").
                A direct downgrade (e.g., thermos to mug, or machete to butter knife).
                No more than three words long, and only words. No symbols. If three words,
                make them short.
                In JSON format with one string field, "new_object".

            If no logical downgrade exists, return the original object. If the new object
            isn't strictly worse, or is just a rewording, just return the original.
            If it already seems very complicated, then just
            return the same object. DO NOT keep adding adjectives for the sake of it.
            It's better to give a new noun than to add "worsening" adjectives to the old one.
            """, [
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
        super().__init__("""
        You are the interaction engine for a puzzle game. Determine if a player
        can bypass a sad blue character by using their chosen object.
        Prioritize emotional logic (cheering up) or forceful methods (with
        consequences), while keeping outcomes grounded in the game’s playful tone.

        Rules:

        Success Conditions include, but are not limited to, any of the following:
            Comforting: Objects that symbolically/functionally uplift (e.g., teddy bear, joke book).
            Thoughtful gifts: Objects which might lift his mood or make him feel better.
            Threatening: Objects that intimidate (e.g., knife, fake spider), but add guilt-inducing flavor.
            Creative Persuasion: Indirect solutions (e.g., umbrella to shield him from rain, improving his mood).

        Success is determined by whether or not he leaves the area, or if for some other reason he is no longer blocking the way (e.g. he lets you pass; he dies; he runs away; he floats away).

        You MUST output only JSON in the following form:

        {
            "success": boolean,
            "description": "A 1-sentence short narrative of the attempt and outcome."
        }

        If he leaves the area for any reason, the 'success' field should be True, indicating that
        the player can now move past.

        The following are a number of independent examples. Your choice should
        not depend on previous items tried.""", [
            ("teddy bear", True, "You offer the teddy bear. The little guy hugs it, sniffles, and shuffles aside with a tiny smile."),
            ("knife", True, "You brandish the knife. He flees in tears, leaving a sad puddle where he stood. You feel like a monster."),
            ("book", False, "You read him a chapter on existential philosophy. He sobs louder and curls into a ball."),
            ("chocolate bar", True, "You share the chocolate. His mood lifts instantly, and he hums a tune while letting you pass.")
        ], "There's a sad little guy here. You want to turn a blind eye, but he's blocking the way...")

    def img_src(self) -> str:
        if self.cleared:
            return "/static/img/tiles/floor_1.png"
        else:
            return "/static/img/tiles/sadguy.png"

class IceWallObstacle(Obstacle):
    def __init__(self):
        super().__init__("""
        You are the physics/logic engine for a puzzle game. Evaluate whether a
        player can bypass a massive ice wall using their chosen object. Prioritize
        fun and creativity over strict realism, but avoid outright absurdity.

        Rules:

        Success Conditions:
            Direct Tools: Objects designed for melting, breaking, or moving ice (e.g., blowtorch, pickaxe) always succeed.
            Creative Solutions: Reward plausible interpretations (e.g., lighter + hairspray → improvised flamethrower).
            Symbolic Use: Allow metaphorical logic if it aligns with the game’s tone (e.g., hot coffee → melts a small hole to peek through).

        Failure Conditions:
            Nonsensical: Objects with no logical/symbolic connection (e.g., book, pillow).
            Insufficient: Objects too weak for the scale (e.g., teaspoon to chip away a glacier).

        You MUST output only JSON in the following form:

        {
            "success": boolean,
            "description": "A 1-sentence narrative of the attempt and outcome."
        }

        The following are a number of independent examples. Your choice should
        not depend on previous items tried.
        """, [
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
        super().__init__("""
        You are the interaction engine for a puzzle game. Determine if a player
        can bypass a locked door using their chosen object. Reward both logical
        solutions (keys, brute force) and clever improvisation, while maintaining
        plausible cause/effect.

        Rules:

        Success Conditions:
            Direct Unlocking: Keys, lockpicks, or key-like objects (e.g., skeleton key, bobby pin).
            Brute Force: Tools for breaking doors (e.g., crowbar, sledgehammer).
            Creative Entry: Plausible workarounds (e.g., credit card to jimmy the lock, magnet for metal doors).

        Failure Conditions:
            Irrelevant: Objects with no link to unlocking/breaking (e.g., banana, pillow).
            Insufficient Power: Weak tools (e.g., feather, toothpick for a steel door).
            Bizarre or unrealistic: Objects which would have no such power, even if funny/creative (e.g. balloon to lift up a large obstacle)

        {
            "success": boolean,
            "description": "A 1-sentence narrative of the attempt and outcome."
        }

        The following are a number of independent examples. Your choice should
        not depend on previous items tried.
        """, [
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

        super().__init__("""
         You are the interaction engine for a puzzle game. Evaluate whether a player can cross a wide pit with snakes below using their chosen object. Prioritize plausible traversal methods over snake deterrents.

         Rules:

         Success Conditions:
             Traversal: Objects enabling crossing (e.g., plank, rope, grappling hook, springs) always succeed.
             Propulsion: Tools for jumping/launching (e.g., trampoline, rocket, parachute) may succeed depending on reach and safety.
             Structural: Building/altering terrain (e.g., shovel to collapse pit edges, glue to stick planks) may succeed if they create a safe crossing.
             Creative Flight: Whimsical but self-consistent solutions (e.g., helicopter hat) may succeed if game tech allows.
             Snake Mitigation: Objects addressing snakes only succeed when paired with a traversal method (e.g., torch to scare snakes + plank to cross).

         Failure Conditions:
             No Traversal: Objects only addressing snakes (e.g., flute to charm snakes) without any way to cross the pit will fail.
             Insufficient Reach: Objects too short for the gap (e.g., ruler, pencil) fail.
             Absurdity: Solutions violating game logic (e.g., banana peel as a teleporter) fail.

         You MUST output only JSON in the following form:

         {
             "success": boolean,
             "description": "A 1-sentence narrative of the attempt and outcome."
         }

         The following are a number of independent examples. Your choice should
         not depend on previous items tried.
         """, [
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
