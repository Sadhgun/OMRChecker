import cv2
from pyzbar.pyzbar import decode
import os
import shutil
import datetime
import json

import numpy as np
import pandas as pd
from pathlib import Path
from src.entry import entry_point
from src.utils.interaction import wait_q

def BarcodeReader(file, Projects):
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
        if input("Would you like to enter manually (y/n): ") != 'n':
            #cv2.imshow('Enter barcode', PatientIdImage)
            print(f"Showing '{file}'\nPress Q on image to continue.")
            #wait_q()
            PatientIdText = input("Barcode: ")
        else:
            return 0
    
    #Sort image into input folders
    destDir = "inputs/" + side["Name"] + "/Page" + str(side["Page No"]) + "/"
    if not(os.path.exists(destDir)):
        os.makedirs(destDir)
    dest = destDir + PatientIdText + ".png"
    cv2.imwrite(dest, img)
    Projects.add(side["Name"])
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
    outputsFolder = cwd + "/outputs/"
    time = datetime.datetime.now()
    time_dir = time.strftime("%H:%M:%S--(%d-%b-%Y)")
    if not(os.path.exists("backup/")):
        os.mkdir("backup/")
    dirs = os.listdir(outputsFolder)
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
                            dest = "backup/" + dir + "/" + time_dir + "/inputs/" + page
                            if not(os.path.exists(dest)):
                                os.makedirs(dest)
                            shutil.move(image, dest)
        projectName = outputsFolder + dir
        if os.path.isdir(projectName):
            subDirs = os.listdir(projectName)
            for page in subDirs:
                pageNo = projectName + "/" + page
                if os.path.isdir(pageNo):
                    dest = "backup/" + dir + "/" + time_dir + "/outputs/" + page
                    shutil.move(pageNo, dest)

def CheckForOthers(project, page, item, x1, x2, y1, y2):
    OutputFolder = os.getcwd() + "/outputs/" + project + "/" + page
    csv = OutputFolder + "/Results/Results.csv"
    df = pd.read_csv(csv)
    if item in list(df.columns):
        others = df.loc[df[item] == 1]
        others = others["output_path"].tolist()
        for image in others:
            img = cv2.imread(image)
            img = img[x1:x2, y1:y2]
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

def CallForOthers(Projects):
    for project in Projects:
        file = "config-json/" + project + ".json"
        opened = open(file)
        loaded = json.load(opened)
        total_pages = loaded["total-pages"]
        for i in range(1, total_pages + 1, 1):
            page = f"Page{i}"
            Page = loaded[page]
            if Page["has-others"] == "yes":
                Others = Page["others"]
                for item in Others:
                    x1, x2, y1, y2 = Others[item]['x1'], Others[item]['x2'], Others[item]['y1'], Others[item]['y2']
                    CheckForOthers(project, page, item, x1, x2, y1, y2)

if __name__ == "__main__":
    folder = "add-files/"
    files = os.listdir(folder)
    Projects = set()

    for file in files:
        if file.endswith('.png'):
            BarcodeReader(file, Projects)
    MissingFileChecker()
    ans = str(input("Would you like to continue (y/n): "))
    if ans != 'n':
        entry_point(Path('inputs'), {'input_paths': ['inputs'], 'debug': True, 'output_dir': 'outputs', 'autoAlign': False, 'setLayout': False})
        CallForOthers(Projects)
        BackupImages()