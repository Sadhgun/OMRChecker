import os
from PIL import ImageDraw, Image, ImageFont
from src.extras.qrcodeGen import QRGenerate

if __name__ == "__main__":
    name = input("Enter name of study: ")
    pages = int(input("Enter number of pages: "))
    marker = Image.open("required-files/omr_marker.jpg")
    marker.thumbnail((60, 60))

    if not(os.path.exists(f"Forms/{name}")):
        os.mkdir(f"Forms/{name}")

    for i in range(1, pages + 1):
        page = Image.new(mode = "RGB", size = (827, 1169), color = (255, 255, 255))
        page.show("Page")
        page.paste(marker, (0, 0))
        page.paste(marker, (767, 0))
        page.paste(marker, (0, 1109))
        page.paste(marker, (767, 1109))
        QRCode = QRGenerate(name, i)
        page.paste(QRCode, (700, 200))
        dest = f'Forms/{name}/Page{i}.png'
        page.save(dest)