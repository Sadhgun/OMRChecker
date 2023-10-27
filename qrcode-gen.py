import qrcode
from PIL import ImageDraw, Image

qr = qrcode.QRCode(
    version=10,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=5
)
qr.add_data('[Name: Symptom Registry; Page No: 1]')
qr.make()
img = qr.make_image(fill_color="black", back_color="white")
width, height = img.size
box = Image.new(mode="RGB", size=(width, height + 50), color = (255, 255, 255))
box.paste(img, (0, 0))
draw = ImageDraw.Draw(box)
draw.multiline_text((width // 2, height), 'Page No: 1', fill=0)
box.save('qrcode_test.png')