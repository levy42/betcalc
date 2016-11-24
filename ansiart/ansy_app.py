import os
import uuid
from flask import Flask, render_template, request
import ansi_art as art

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

PALETTES = art.PALETTE_MAP.keys()
BLOCK_SIZES = [3, 4, 5, 7, 10, 15, 20, 25, 30, 40, 50]


@app.route("/")
def index():
    return render_template("index.html", block_sizes=BLOCK_SIZES,
                           palettes=PALETTES)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files.get('file')
        block_size = int(request.form['block-size'])
        inverse = True if request.form.get('inverse') else False
        palette = request.form['palette']
        filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
        f.save(filename)
        text_image = art.get_art(filename, b_size=block_size, inverse=inverse,
                                 palette=art.PALETTE_MAP[palette])
        os.remove(filename)
        return render_template("index.html", image=text_image, inverse=inverse,
                               block_sizes=BLOCK_SIZES,
                               palettes=PALETTES)


app.run(port=4000, host='0.0.0.0')