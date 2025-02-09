import json
import ollama

schema = {
    "title": "Upgrade machine result",
    "description": "A structured response about the output of an upgrade machine.",
    "type": "object",
    "properties": {
        "new_object": {"type": "string"}
    },
    "required": "new_object"
}

messages=[
    {
        "role": "system",
        "content": """
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
        """
    },
    {
        "role": "user", "content": "butter knife",
    },
    {
        "role": "assistant", "content": '{"new_object": "machete"}'
    },
    {
        "role": "user", "content": "bicycle",
    },
    {
        "role": "assistant", "content": '{"new_object": "motorcycle"}'
    },
    {
        "role": "user", "content": "bucket",
    },
    {
        "role": "assistant", "content": '{"new_object": "waterproof backpack"}'
    },
    {
        "role": "user", "content": "key",
    },
    {
        "role": "assistant", "content": '{"new_object": "master key"}'
    },
    {
        "role": "user", "content": "rock",
    },
    {
        "role": "assistant", "content": '{"new_object": "slingshot"}'
    },
]

while True:
    new_msg =  {
        "role": "user", "content": input("item: "),
    }

    response = ollama.chat(
        model="phi4",
        messages=messages + [new_msg],
        format=schema
    )

    print(response.message.content)
