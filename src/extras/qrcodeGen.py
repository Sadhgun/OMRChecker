import qrcode
import os
from PIL import ImageDraw, Image, ImageFont

def QRGenerate(qrStr, textStr):
    qr = qrcode.QRCode(
        version=None, #TODO: Check version options
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=0
    )
    qr.add_data(qrStr)
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")
    width, height = img.size
    box = Image.new(mode="RGB", size=(width, height + 60), color = (255, 255, 255)) #TODO: Check required resolution
    box.paste(img, (0, 0))
    draw = ImageDraw.Draw(box)
    font = ImageFont.truetype(r'required-files/Roboto-Regular.ttf', 60)
    dimensions = draw.textbbox((0, 0), textStr, font=font)
    draw.multiline_text(((width - dimensions[2]) // 2, height - 10), textStr, fill=0, font=font)
    return box

if __name__ == "__main__":
    name = input("Enter name of study: ")
    pages = int(input("Enter number of pages: "))

    if not(os.path.exists(f"QRCodes/{name}")):
        os.mkdir(f"QRCodes/{name}")
    for i in range(1, pages + 1):
        qrStr = str({"Name": name, "Page No": i})
        textStr = f'Page No: {i}'
        box = QRGenerate(qrStr, textStr)
        dest = f'QRCodes/{name}/Page{i}.png'
        box.save(dest)