import qrcode
import os
from PIL import ImageDraw, Image, ImageFont

name = input("Enter name of study: ")
pages = int(input("Enter number of pages: "))

if not(os.path.exists(f"QRCodes/{name}")):
        os.mkdir(f"QRCodes/{name}")

for i in range(1, pages + 1):
    qr = qrcode.QRCode(
        version=None, #TODO: Check version options
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=0
    )
    qrInfo = {"Name": name, "Page No": i}
    qr.add_data(str(qrInfo))
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")
    width, height = img.size
    box = Image.new(mode="RGB", size=(width, height + 70), color = (255, 255, 255)) #TODO: Check required resolution
    box.paste(img, (0, 0))
    draw = ImageDraw.Draw(box)
    font = ImageFont.truetype(r'required-files/Roboto-Regular.ttf', 60)
    dimensions = draw.textbbox((0, 0), f'Page No: {i}', font=font)
    draw.multiline_text(((width - dimensions[2]) // 2, height - 10), f'Page No: {i}', fill=0, font=font)
    dest = f'QRCodes/{name}/Page{i}.png'
    box.save(dest)