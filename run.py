import cv2
from pyzbar.pyzbar import decode
import os
import shutil
import numpy as np

def BarcodeReader(img):
    y, x, z = img.shape
    SideImage = img[0:y // 2, x // 2:x] #Reads page side
    side = decode(SideImage)
    if len(side) == 1:
        side = ((side[0]).data).decode("utf-8")
    else:
        if y / x >= 1: #Checks if page is vertical
            img = cv2.rotate(img, cv2.ROTATE_180)
            SideImage = img[0:y // 2, x // 2:x]
            side = decode(SideImage)
        side = ((side[0]).data).decode("utf-8")

    PatientIdImage = img[0:y // 2, 0:x // 2] #Reads patient id
    PatientId = decode(PatientIdImage)
    if len(PatientId) == 1:
        PatientIdText = ((PatientId[0]).data).decode("utf-8")
        img = cv2.polylines(img, [np.array(PatientId[0].polygon)], True, (0, 255, 0), 5)
        write = "Read barcode: " + PatientIdText
        img = cv2.putText(img, write, (100, 260), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3, cv2.LINE_AA)
    else:
        print(f"Barcode not found: {image}")
        if input("Would you like to enter manually: ") == 'y':
            #cv2.imshow('Enter barcode', PatientIdImage)
            #cv2.waitKey(0)
            PatientId = input("Barcode: ")
        else:
            return 0
    
    #Sort image into input folders
    if side == 'Back':
        dest = "inputs/back/" + PatientIdText + ".png"
    elif side == 'Front':
        dest = "inputs/front/" + PatientIdText + ".png"
    cv2.imwrite(dest, img)
    return 1

def MissingFileChecker():
    FrontFolder = "inputs/front/"
    BackFolder = "inputs/back/"

    fronts = os.listdir(FrontFolder)
    backs = os.listdir(BackFolder)

    print('Backs missing: ', end="")
    print(list(set(fronts).difference(backs)))

    print('Fronts missing: ', end="")
    print(list(set(backs).difference(fronts)))
 
def BackupImages():
    FrontsFolder = "inputs/front/"
    BacksFolder = "inputs/back/"
    FrontBackup = "backup/inputs/front/"
    BackBackup = "backup/inputs/back/"
    if not(os.path.exists("backup/")):
        os.mkdir("backup/")
        os.mkdir("backup/inputs/")
    if not(os.path.exists("backup/inputs/")):
        os.mkdir("backup/inputs/")
    if not(os.path.exists(FrontBackup)):
        os.mkdir(FrontBackup)
    if not(os.path.exists(BackBackup)):
        os.mkdir(BackBackup)
    for file in os.listdir(FrontsFolder):
        if file.endswith('.png'):
            src = FrontsFolder + file
            shutil.move(src, FrontBackup)
    for file in os.listdir(BacksFolder):
        if file.endswith('.png'):
            src = BacksFolder + file
            shutil.move(src, BackBackup)

if __name__ == "__main__":
    folder = "add-files/"
    files = os.listdir(folder)

    if not(os.path.exists("inputs/front/")):
        os.mkdir("inputs/front/")
    if not(os.path.exists("inputs/back/")):
        os.mkdir("inputs/back/")

    for file in files:
        if file.endswith('.png'):
            image = "add-files/" + file
            img = cv2.imread(image)
            BarcodeReader(img)

    MissingFileChecker()
    ans = str(input("Would you like to continue (y/n): "))
    if ans == 'y':
        os.system("python main.py")
        BackupImages()