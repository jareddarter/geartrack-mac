import barcode
from barcode.writer import ImageWriter
import qrcode

def generate_code128(data, filepath):
    code128 = barcode.get('code128', data, writer=ImageWriter())
    code128.save(filepath)

def generate_qr(data, filepath):
    img = qrcode.make(data)
    img.save(filepath)
