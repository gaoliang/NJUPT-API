import json
from io import BytesIO

import requests
from PIL import Image

from njupt import Library
from njupt.utils.captchas import build_vector
from njupt.utils.captchas.library.libray_captcha import LibraryCaptcha

if __name__ == "__main__":
    image_data = []

    for i in range(10):
        r = requests.get(Library.URLs.CAPTCHA)
        im = Image.open(BytesIO(r.content))
        im.show()
        captcha = LibraryCaptcha(image=im)
        letters = input()
        for letter, im in zip(letters, captcha.handle_split_image()):
            vector = build_vector(im)
            image_data.append({letter: vector})

    with open('image_data.json', 'w') as f:
        json.dump(image_data, f)
