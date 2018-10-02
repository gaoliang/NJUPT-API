import json
import os
from io import BytesIO

import requests
from PIL import Image

from njupt.utils.captchas import distance_hanmming, build_vector

BLACK = 0
WHITE = 255

current_dir = os.path.dirname(os.path.abspath(__file__))


class LibraryCaptcha:

    def __init__(self, image):
        self.image = image.convert('1')

    def handle_split_image(self):
        # 切割验证码，返回包含四个字符图像的列表
        y_min, y_max = 16, 26
        split_lines = [4, 16, 28, 40, 52]
        ims = [self.image.crop([u, y_min, v, y_max]) for u, v in zip(split_lines[:-1], split_lines[1:])]
        return ims

    def crack(self):
        result = []
        # 加载数据
        with open(os.path.join(current_dir, 'image_data.json'), 'r') as f:
            image_data = json.load(f)
        for letter in self.handle_split_image():
            letter_vector = build_vector(letter)
            guess = []
            for image in image_data:
                for x, y in image.items():
                    guess.append((distance_hanmming(y, letter_vector), x))
            guess.sort()
            result.append(guess[0][1])
        return ''.join(result)

    def __str__(self):
        return self.crack()


if __name__ == "__main__":
    from njupt import Library

    r = requests.get(Library.URLs.CAPTCHA)
    im = Image.open(BytesIO(r.content))
    im.show()
    captcha = LibraryCaptcha(image=im)
    print(captcha.crack())
