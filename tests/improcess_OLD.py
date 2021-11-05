import cv2
import imutils
import numpy as np
import easyocr

def find_licenseplate(imgName):
    #reading image & variable assignment
    img = cv2.imread(imgName)
    height=img.shape[0]
    width=img.shape[1]
    scale_percent=100
    max_height = 1300
    #resize image if the image is t
    while height > max_height:
        print(scale_percent)
        scale_percent -= 5
        new_height = int(height * scale_percent / 100)
        new_width = int(width * scale_percent / 100)
        if new_height < max_height:
            dsize = (new_width, new_height)
            img = cv2.resize(img, dsize)
            break
    
    #hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    light_yellow = np.array([160, 255, 255])
    dark_yellow = np.array([0, 100, 100])
    mask = cv2.inRange(img, dark_yellow, light_yellow)
    output = cv2.bitwise_and(img,img, mask= mask)
    #applying filters to image
    gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3,3), 0)
    edged = cv2.Canny(blurred, 100, 255)
    
    #get the top 15 contours
    contours = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
    #look for rectangle within contours
    location = []
    for c in contours:
        approx = cv2.approxPolyDP(c, 10, True)
        if len(approx) == 4:
            location = approx
            break
        
    #temp if statement
    if len(location) == 0:
        cv2.imshow("failed", edged)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return {"error": "No license plate found"}

    #create a mask of the licenseplate area
    mask = np.zeros(blurred.shape,np.uint8)
    mask = cv2.drawContours(mask,[location],0,255,-1,)

    #crop to mask
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    cropped = gray[topx:bottomx+1, topy:bottomy+1]
    
    #apply blackhat filter in order ot make the characters more visible
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18,8))
    cropped = cv2.morphologyEx(cropped, cv2.MORPH_BLACKHAT, kernel)
    #read image text with easyocr
    result = reader.readtext(cropped)
    #plate = result[0][1].replace(" ", "-")
    print(result)

    img = cv2.drawContours(img,[location],0,(0,255,0),2,)
    cv2.imshow("img", img)
    cv2.imshow("image", cropped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


reader = easyocr.Reader(["en"])

find_licenseplate("images/fail4.png")
find_licenseplate("images/testimg43.jpg")
find_licenseplate("images/testimg2.jpg")
find_licenseplate("images/testmclaren.jpg")
find_licenseplate("images/fail3.png")
find_licenseplate("images/fail2.png")
find_licenseplate("images/real1.jpg")
find_licenseplate("images/real2.jpg")
find_licenseplate("images/real3.jpg")
