from app import app
from flask import render_template, request, redirect, jsonify, make_response
import os
from werkzeug.utils import secure_filename
from main import CompletedModel
import cv2
import time
from PIL import Image
import numpy as np


app.config["IMAGE_UPLOADS"] = "app/static/img/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024


def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


def infer(image):
    model = CompletedModel.get_instance()
    start = time.time()
    output = model.predict(image, is_Front=True, infer=True)
    end = time.time()
    print("Inference time 's model: ", end - start)
    return output


@app.route("/", methods=["GET", "POST"])
def upload_image():
    return render_template("public/upload_image.html")


@app.route("/upload-image", methods=["POST"])
def create_entry():
    if request.method == "POST":
        if request.files:
                image = request.files["fileCar"]
                if image.filename == "":
                    print("No filename")
                    return redirect(request.url)

                if allowed_image(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                    img_PIL = Image.open(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                    img_PIL = img_PIL.resize((640, 640), Image.ANTIALIAS)
                    img = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
                    field_dict = infer(img)
                    res = make_response(jsonify(field_dict), 200)
                    return res
                else:
                    print("That file extension is not allowed")
                    return redirect(request.url)









