import cv2
from pyzbar.pyzbar import decode
import os
#import shutil
#import datetime
#import json

import numpy as np
#import pandas as pd
#from pathlib import Path
#from src.entry import entry_point
from src.utils.interaction import wait_q

def BarcodeReader(file):
    image = "Cropped/" + file
    img = cv2.imread(image)
    imgRead = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    #imgRead = cv2.threshold(imgRead, 0, 255, cv2.THRESH_OTSU)[1]
    #imgRead = cv2.threshold(imgRead, 127, 255, cv2.THRESH_BINARY)[1]
    y, x = imgRead.shape
    SideImage = imgRead[0:y // 2, x // 2:x] #Reads page side
    side = decode(SideImage)
    if len(side) == 1:
        side = eval((side[0].data).decode("utf-8"))
    else: 
        if y / x >= 1: #Checks if page is vertical
            imgRead = cv2.rotate(imgRead, cv2.ROTATE_180)
            img = cv2.rotate(img, cv2.ROTATE_180)
            SideImage = imgRead[0:y // 2, x // 2:x]
            side = decode(SideImage)
        side = eval(((side[0]).data).decode("utf-8"))
        

    PatientIdImage = imgRead[0:y // 2, 0:x // 2] #Reads patient id
    PatientId = decode(PatientIdImage)
    if len(PatientId) == 1:
        PatientIdText = ((PatientId[0]).data).decode("utf-8")
    else:
        print(f"Barcode not found: {file}")
        if input("Would you like to enter manually (y/n): ") != 'n':
            cv2.imshow('Enter barcode', PatientIdImage)
            print(f"Showing '{file}'\nPress Q on image to continue.")
            wait_q()
            PatientIdText = input("Barcode: ")
        else:
            return 0

    img = cv2.polylines(img, [np.array(PatientId[0].polygon)], True, (0, 255, 0), 5)
    write = "Read barcode: " + PatientIdText
    img = cv2.putText(img, write, (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3, cv2.LINE_AA)
    
    #Sort image into input folders
    destDir = "inputs/" + side["Name"] + "/Page" + str(side["Page No"]) + "/"
    if not(os.path.exists(destDir)):
        os.makedirs(destDir)
    dest = destDir + PatientIdText + ".png"
    cv2.imwrite(dest, img)
    os.remove(image)
    return PatientIdText, side["Name"]

if __name__ == "__main__":
    Projects = set()
    for file in os.listdir("Cropped"):
        if file.endswith(".png"):
            PatientId, project = BarcodeReader(file)
            Projects.add(project)
            print(PatientId)
    print(f"Projects: {Projects}")
    print("Finished reading barcodes.")