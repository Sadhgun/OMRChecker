import cv2
import os
import shutil
import datetime
import json

import numpy as np
import pandas as pd
from pathlib import Path
from src.entry import entry_point
from src.utils.interaction import wait_q
from src.extras.cropping import Cropper
from barcodeReader import BarcodeReader

def MissingFileChecker():
    cwd = os.getcwd()
    inputsFolder = cwd + "/inputs/"
    if not(os.path.exists("backup/")):
        os.mkdir("backup/")
    dirs = os.listdir(inputsFolder)
    for dir in dirs:
        projectName = inputsFolder + dir
        if os.path.isdir(projectName): # if not os.path.isdir(projectName): continue
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
        for i in range(totalPages): # Make a seperate function for this
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

def CaptureOthersBox(project, page, item, x1, x2, y1, y2):
    OutputFolder = os.getcwd() + "/outputs/" + project + "/" + page
    csv = OutputFolder + "/Results/Results.csv"
    df = pd.read_csv(csv)
    others = df.loc[df[item] == 1]
    others = others["output_path"].tolist()
    for image in others:
        img = cv2.imread(image)
        img = img[x1:x2, y1:y2]
        if input(f"Would you like to enter other image text manually for {image} (y/n): ") != 'n':
            cv2.imshow('Enter text', img)
            print(f"Showing '{image}'\nPress Q on image to continue.")
            wait_q()
            text = input("Enter text: ")
        dest = csv.replace("Results/Results.csv", "")
        dest = dest.replace(os.getcwd(), "")
        image = "/" + image
        image = image.replace(dest, "")
        image = image.replace("CheckedOMRs", "")
        dest = dest + "OthersFolder/" + item # TODO: Check if itmoves to a subfolder in OthersFolder
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
                    CaptureOthersBox(project, page, item, x1, x2, y1, y2)

def MasterResults(Projects):
    for project in Projects:
        folder = "Results/" + project
        if not(os.path.exists(folder)):
            os.mkdir(folder)
        file = folder + "/Master-Result.csv"
        if not(os.path.exists(file)):
            with open(file, 'w') as file:
                file.close
        

if __name__ == "__main__":
    folder = "add-files/"
    files = os.listdir(folder)
    Projects = set()

    for file in files:
        if file.endswith('.png'):
            print(file)
            imageFile = folder + file
            destFile = "Cropped/" + file
            if Cropper(imageFile, destFile):
                PatientId, projectName = BarcodeReader(file)
                Projects.add(projectName)
                print(PatientId)
                print(projectName)
    MissingFileChecker()
    ans = str(input("Would you like to continue (y/n): "))
    if ans != 'n':
        entry_point(Path('inputs'), {'input_paths': ['inputs'], 'debug': True, 'output_dir': 'outputs', 'autoAlign': False, 'setLayout': False})
        CallForOthers(Projects)
        MasterResults(Projects)
        BackupImages()