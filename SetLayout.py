import cv2
import os
from src.entry import entry_point
from pathlib import Path

def DrawGrids(img):
    y, x, z = img.shape
    color = (0, 0, 0)
    thickness = 1
    for i in range(0, x, 20):
        StartPoint = (i, 0)
        EndPoint = (i, y)
        img = cv2.line(img, StartPoint, EndPoint, color, thickness)
    for i in range(0, y, 20):
        StartPoint = (0, i)
        EndPoint = (x, i)
        img = cv2.line(img, StartPoint, EndPoint, color, thickness)
    return img


if __name__ == "__main__":
    folder = "inputs/Symptom Registry/Page1/"
    files = os.listdir(folder)
    for file in files:
        if file.endswith("SetLayout.png"):
            file = folder + file
            os.remove(file)
        elif file.endswith("SetLayoutGrids.png"):
            file = folder + file
            os.remove(file)
    entry_point(Path('inputs'), {'input_paths': ['inputs'], 'debug': True, 'output_dir': 'outputs', 'autoAlign': False, 'setLayout': True})
    for file in files:
        if file.endswith("SetLayout.png"):
            file = folder + file
            img = cv2.imread(file)
            image = file.replace("SetLayout.png", "SetLayoutGrids.png")
            cv2.imwrite(image, DrawGrids(img))