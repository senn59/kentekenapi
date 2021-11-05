from flask import Flask, request, Response
import werkzeug
import cv2
import imutils
import numpy as np
import easyocr
import requests
from processor import Image

app = Flask(__name__)
@app.route("/scanner", methods=["POST"])
def scanner():
    file = request.files["image"]
    imgBytes = file.read()
    imgNP = np.frombuffer(imgBytes, np.uint8)
    img = cv2.imdecode(imgNP, cv2.IMREAD_ANYCOLOR)
    return Image(img).output

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")