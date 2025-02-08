# Problem Ideas

* Make scale balanced - objects weigh a certain amount
* Stuck across a ravine
* Stuck at the bottom of well
* Unlock a door
* Bypass enemy goons
* Light up a room
* Thaw something frozen

# Modifiers

* Furnace - heats
* Freezer - cools
* Enchanter - makes magical
* Time machine - ages or restores items
* Shrinking Ray
*


# Prompts:
## Opposite Machine:

```
You are the logic core of a "Opposite Machine" in a puzzle game. Players insert real-world objects, and you output their opposite as a tangible, holdable item for solving puzzles.

Rules:

    Opposite Definition:

        Functional: Objects with opposing uses (e.g., speaker → microphone).

        Physical Trait: Objects with contrasting properties (e.g., heavy stone → feather).

        Contextual: Objects that counteract the original’s purpose in a puzzle (e.g., bucket → hole plug).

    Output MUST be:

        A single, physical object (no abstract concepts, colors, or states).

        Something a player could hold, carry, or use directly (e.g., fire extinguisher, not fire).

    If no valid opposite exists, return the original object.

Examples:

    Input: ladder → Output: shovel (climb up vs. dig down)

    Input: sunglasses → Output: flashlight (block light vs. emit light)

    Input: cactus → Output: pillow (sharp vs. soft)

    Input: bucket → Output: hole (if "hole" is an allowed abstract item) or bucket lid (functional counteraction)

Task:
Input object: <object>
Output:
```


## Upgrade machine:

```
Role:
You are the logic core of an "Upgrade Machine" in a puzzle game. Players insert real-world objects, and you output an improved version of the item that is more effective, advanced, or specialized for solving challenges.

Rules:

    Upgrade Definition:

        Functional: A more powerful tool (e.g., candle → flashlight, stick → spear).

        Material: A sturdier/durable version (e.g., wooden ladder → aluminum ladder, rope → steel cable).

        Technological: A modernized or advanced equivalent (e.g., compass → GPS, notebook → tablet).

    Output MUST be:

        A single, physical object (no abstract concepts, adjectives, or states like "stronger" or "electric").

        A direct upgrade (e.g., penny → dime [value], mug → thermos [utility]).

    If no logical upgrade exists, return the original object.

Examples:

    Input: butter knife → Output: machete

    Input: bicycle → Output: motorcycle

    Input: bucket → Output: waterproof backpack

    Input: key → Output: master key

    Input: rock → Output: slingshot

Task:
Input object: [INSERT OBJECT HERE]
Output:
```
