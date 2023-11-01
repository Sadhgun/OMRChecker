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
        side = eval(((side[0]).data).decode("utf-8"))
    else:
        if y / x >= 1: #Checks if page is vertical
            img = cv2.rotate(img, cv2.ROTATE_180)
            SideImage = img[0:y // 2, x // 2:x]
            side = decode(SideImage)
        side = eval(((side[0]).data).decode("utf-8"))

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
    #print(side["Name"], side["Page No"])
    destDir = "inputs/" + side["Name"] + "/Page" + str(side["Page No"]) + "/"
    if not(os.path.exists(destDir)):
        os.makedirs(destDir)
    dest = destDir + PatientIdText + ".png"
    cv2.imwrite(dest, img)
    return 1

def MissingFileChecker():
    cwd = os.getcwd()
    inputsFolder = cwd + "/inputs/"
    if not(os.path.exists("backup/")):
        os.mkdir("backup/")
    dirs = os.listdir(inputsFolder)
    for dir in dirs:
        projectName = inputsFolder + dir
        if os.path.isdir(projectName):
            imageLists = []
            subDirs = os.listdir(projectName)
            subDirs.sort()
            for page in subDirs:
                pageNo = projectName + "/" + page
                if os.path.isdir(pageNo):
                    files = os.listdir(pageNo)
                    imageList = []
                    for file in files:
                        if file.endswith(".png"):
                            imageList.append(file)
                    imageLists.append(imageList)
    totalPages = len(imageLists)
    differenceDict = {}
    for i in range(totalPages):
        for n in range(i + 1, totalPages):
            frontDiff = list(set(imageLists[n]).difference(imageLists[i]))
            backDiff = list(set(imageLists[i]).difference(imageLists[n]))
            if differenceDict.get(i + 1) is not None:
                differenceDict[i + 1] += frontDiff
            else:
                differenceDict[i + 1] = frontDiff
            if differenceDict.get(n + 1) is not None:
                differenceDict[n + 1] += backDiff
            else:
                differenceDict[n + 1] = backDiff
    for key in differenceDict:
        print(f"Page {key} of {sorted(list(set(differenceDict[key])))} are missing.")
 
def BackupImages():
    cwd = os.getcwd()
    inputsFolder = cwd + "/inputs/"
    if not(os.path.exists("backup/")):
        os.mkdir("backup/")
    dirs = os.listdir(inputsFolder)
    for dir in dirs:
        projectName = inputsFolder + dir
        if os.path.isdir(projectName):
            subDirs = os.listdir(projectName)
            for page in subDirs:
                pageNo = projectName + "/" + page
                if os.path.isdir(pageNo):
                    files = os.listdir(pageNo)
                    for file in files:
                        if file.endswith('.png'):
                            image = pageNo + "/" + file
                            dest = "backup/inputs/" + dir + "/" + page
                            if not(os.path.exists(dest)):
                                os.makedirs(dest)
                            shutil.move(image, dest)
    #TODO: Move output files

if __name__ == "__main__":
    folder = "add-files/"
    files = os.listdir(folder)

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