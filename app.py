import json
from flask import Flask, request, send_from_directory
from flask_compress import Compress
from PIL import Image
from io import BytesIO
from src.encoding import Provider

import src.game as game
import src.llm as llm

import ollama
import base64

app = Flask(__name__, static_folder='static')
app.json = Provider(app=app)
Compress(app)

state = game.State(8, 8)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.get("/api/state")
def get_state():
    return {
        "state": state,
    }, 200

@app.post("/api/move-player/<direction>")
def move_player(direction: str):
    if direction not in ['l', 'r', 'u', 'd']:
        return { "error": "Invalid direction" }, 400

    success, msg = state.move_player(direction)
    return {
        "ok": success,
        "message": msg,
    }, 200

@app.post("/api/select-item/<int:index>")
def select_item(index: int):
    return {
        "ok": state.player.select_item(index)
    }, 200

@app.post("/api/upload-image")
def upload_image():
    data = request.get_json()
    base64_image = data.get("image")
    image_data = base64.b64decode(base64_image)

    print(f"got image data: {len(image_data)}B")

    image = Image.open(BytesIO(image_data))
    image.thumbnail((350, 350))
    image.save("static/img/image.png")

    print("image saved")

    resp = llm.chat([
        {
            "role": "user",
            "content": llm.photo_prompt,
            "images": [ "./static/img/image.png" ]
        }
    ], schema=llm.photo_schema)

    print("all done")

    if (content := resp.message.content) is None:
        return { "ok": False, "message": "Something went wrong" }, 400

    obj = json.loads(content).get("object", None)
    if obj is None:
        return { "ok": False, "message": "Try looking at something useful, loser." }

    added = state.summon_item(obj)
    if not added:
        return { "ok": False, "message": "Looks like you're a little overburdened there already, buddy." }

    return {
        "ok": True,
        "message": f"The Gods Above bring forth unto you: {obj}"
    }

if __name__ == '__main__':
    app.run(
        debug=True,
        host="0.0.0.0", port=443,
        ssl_context=("localhost+2.pem", "localhost+2-key.pem")
    )
