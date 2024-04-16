# Used to add QR Code as patient marker in forms

from PIL import Image
from src.extras.qrcodeGen import QRGenerate
import csv

#Individual forms with no csv

if __name__ == "__main__":
    form = "Forms/Symptom Registry JSS/Page1/OMR Sheet.png"
    start = int(input("Start number: "))
    end = int(input("End number: "))
    csvfile = open(f"Forms/Symptom Registry JSS/CSVs/List{start}-{end}.csv", 'w')
    headers = ["QR Code", "Patient ID"]
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(headers)
    for i in range(start, end + 1):
        box = QRGenerate(str(i), str(i))
        box.thumbnail((110, 110))
        blankForm = Image.open(form)
        blankForm.paste(box, (70, 38))
        dest = f'Forms/Symptom Registry JSS/Forms-QR/Patient{i}.png'
        blankForm.save(dest)
        row = [str(i), ""]
        csvwriter.writerow(row)
    
        