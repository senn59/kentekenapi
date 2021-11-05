import cv2
import imutils
import numpy as np
import easyocr
import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("API_KEY")
reader = easyocr.Reader(["en"])

class Image:
    def __init__(self, img):
        #read image and get image data
        self.img = self.resize_img(img) #read image and resize if needed
        self.process_img([0,110,110], [150,255,255]) #applies filter to images
        self.location = self.get_plate_contour() #license plate location on the image
        if not self.location.any():
            self.process_img([0,100,100], [160,255,255])
            self.get_plate_contour()
            if not self.location.any():
                self.output = {"error": "Geen kenteken gevonden"}
                return
        self.cropped = self.crop_img()
        self.output = self.extract_text()

    def resize_img(self, img):
        height=img.shape[0]
        width=img.shape[1]
        #resize image if the image is too big to cut down processing speed
        scale_percent=100
        max_height = 1300
        while height > max_height:
            scale_percent -= 5
            new_height = int(height * scale_percent / 100)
            new_width = int(width * scale_percent / 100)
            if new_height < max_height:
                dsize = (new_width, new_height)
                img = cv2.resize(img, dsize)
                break
        return img

    def process_img(self, dark_bgr, light_bgr):
        #filter out yellow
        img = self.img
        dark_yellow = np.array(dark_bgr)
        light_yellow = np.array(light_bgr)
        mask = cv2.inRange(img, dark_yellow, light_yellow)
        output = cv2.bitwise_and(img,img, mask= mask)
        #applying filters to image
        gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3,3), 0)
        edged = cv2.Canny(blurred, 100, 255)
        #init attributes
        self.gray = gray
        self.blurred = blurred
        self.edged = edged

    def get_plate_contour(self):
        #get the top 15 contours
        contours = cv2.findContours(self.edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
        #look for rectangle within contours
        location = []
        for c in contours:
            approx = cv2.approxPolyDP(c, 10, True)
            if len(approx) == 4:
                location = approx
                break
        #init attribute
        return location

    def crop_img(self):
        #create a mask of the licenseplate area
        mask = np.zeros(self.blurred.shape,np.uint8)
        mask = cv2.drawContours(mask,[self.location],0,255,-1,)
        #crop to mask
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        cropped = self.gray[topx:bottomx+1, topy:bottomy+1]
        #apply blackhat filter in order ot make the characters more visible
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18,8))
        cropped = cv2.morphologyEx(cropped, cv2.MORPH_BLACKHAT, kernel)
        return cropped

    def extract_text(self):
        result = reader.readtext(self.cropped)
        if not result:
            return {"error": "Geen kenteken gevonden"}
        plate = result[0][1].replace(" ", "").replace("-", "").replace(".", "").replace(",", "")
        #make api call to overheidio
        url = "https://api.overheid.io/voertuiggegevens/"
        response = requests.get(url + plate, {"ovio-api-key": key})
        return response.json()
        #return {"license plate": plate}