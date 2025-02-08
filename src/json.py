from typing import Any

from flask.json.provider import JSONProvider

import src.tile as tile
import src.map as map
import src.player as player
import json

class Encoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, tile.Tile):
            o.__dict__.update({
                "class": o.__class__.__name__,
                "img": o.img_src()
            })

        if isinstance(o, player.Player):
            o.__dict__.update({
                "img": o.img_src()
            })

        if isinstance(o, object):
            return o.__dict__

        return super().default(o)

class Provider(JSONProvider):
    def dumps(self, obj: Any, **kwargs: Any) -> str:
        return json.dumps(obj, **kwargs, cls=Encoder)

    def loads(self, s: str | bytes, **kwargs: Any) -> Any:
        return json.loads(s, **kwargs)
