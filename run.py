import cv2
from pyzbar.pyzbar import decode
import os
import shutil
import numpy as np
import pandas as pd
from pathlib import Path

from src.entry import entry_point

def BarcodeReader(file):
    image = "add-files/" + file
    img = cv2.imread(image)
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
        print(f"Barcode not found: {file}")
        if input("Would you like to enter manually (y/n): ") == 'y':
            #cv2.imshow('Enter barcode', PatientIdImage)
            #cv2.waitKey(0)
            PatientIdText = input("Barcode: ")
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
    if totalPages > 1:
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
            if len(sorted(list(set(differenceDict[key])))) > 0:
                print(f"Page {key} of {sorted(list(set(differenceDict[key])))} are missing.")
    else:
        print("Single page project")
 
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

def CheckForOthers():
    OutputFolder = os.getcwd() + "/outputs/"
    Projects = os.listdir(OutputFolder)
    Projects.sort()
    for project in Projects:
        ProjectDir = OutputFolder + project + "/"
        Pages = os.listdir(ProjectDir)
        Pages.sort()
        for page in Pages:
            csv = ProjectDir + page + "/Results/Results.csv"
            df = pd.read_csv(csv)
            if "q15" in list(df.columns):
                others = df.loc[df["q15"] == "yes"]
                others = others["output_path"].tolist()
                for image in others:
                    img = cv2.imread(image)
                    img = img[320:380, 640:970]
                    dest = csv.replace("Results/Results.csv", "")
                    dest = dest.replace(os.getcwd(), "")
                    image = "/" + image
                    image = image.replace(dest, "")
                    image = image.replace("CheckedOMRs", "")
                    dest = dest + "OthersFolder"
                    dest = os.getcwd() + dest
                    if not(os.path.exists(dest)):
                        os.makedirs(dest)
                    dest += image
                    cv2.imwrite(dest, img)

if __name__ == "__main__":
    folder = "add-files/"
    files = os.listdir(folder)

    for file in files:
        if file.endswith('.png'):
            BarcodeReader(file)

    MissingFileChecker()
    ans = str(input("Would you like to continue (y/n): "))
    if ans == 'y':
        entry_point(Path('inputs'), {'input_paths': ['inputs'], 'debug': True, 'output_dir': 'outputs', 'autoAlign': False, 'setLayout': False})
        BackupImages()
        CheckForOthers()