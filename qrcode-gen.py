import qrcode
from PIL import ImageDraw, Image, ImageFont

name = input("Enter name of study: ")
pages = int(input("Enter number of pages: "))

for i in range(1, pages + 1):
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=0
    )
    qrInfo = {"Name": name, "Page No": i}
    qr.add_data(str(qrInfo))
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")
    width, height = img.size
    box = Image.new(mode="RGB", size=(width, height + 60), color = (255, 255, 255))
    box.paste(img, (0, 0))
    draw = ImageDraw.Draw(box)
    font = ImageFont.truetype(r'Roboto-Regular.ttf', 50)
    dimensions = draw.textbbox((0, 0), f'Page No: {i} out of {pages}', font=font)
    draw.multiline_text(((width - dimensions[2]) // 2, height), f'Page No: {i} out of {pages}', fill=0, font=font)
    dest = f'QRCodes/Page{i}.png'
    box.save(dest)