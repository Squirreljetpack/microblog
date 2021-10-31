import base64

def convert_and_save(string, dest):
    with open(dest, "wb") as fh:
        fh.write(base64.decodebytes(string))

def save_image():
    pass