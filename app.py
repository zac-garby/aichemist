from flask import Flask, request, send_from_directory
from PIL import Image
from io import BytesIO

import base64

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.post("/api/upload-image")
def upload_image():
    data = request.get_json()
    base64_image = data.get("image")
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data))
    image.save("static/img/image.png")

    return {
        "path": "/static/img/image.png",
    }, 200

if __name__ == '__main__':
    app.run(debug=True)
