import json
import os
from io import BytesIO

import requests
from PIL import Image

from njupt.utils.captchas import distance_hanmming, build_vector, rotate_img

BLACK = 0
WHITE = 255

current_dir = os.path.dirname(os.path.abspath(__file__))


class ZhengfangCaptcha:
    """
    knn 识别正方验证码
    """

    def __init__(self, image):
        self.image = image
        self.image_pre_process()

    def image_pre_process(self):
        # 去除杂色点
        for x in range(self.image.width):
            for y in range(self.image.height):
                pix = self.image.getpixel((x, y))
                if pix == 43:
                    self.image.putpixel((x, y), WHITE)
                else:
                    self.image.putpixel((x, y), BLACK)

        # 去除单像素噪点并进行二值化(八值法)
        for x in range(self.image.width):
            for y in range(self.image.height):
                count = 0
                if x != 0 and y != 0 and x != self.image.width - 1 and y != self.image.height - 1:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            tx = x + i
                            ty = y + j
                            if self.image.getpixel((tx, ty)) == BLACK:
                                count += 1
                if self.image.getpixel((x, y)) == WHITE and count == 8:
                    self.image.putpixel((x, y), BLACK)
        self.image = self.image.convert('1')

    def handle_split_image(self):
        # 切割验证码，返回包含四个字符图像的列表
        y_min, y_max = 0, 22
        split_lines = [5, 17, 29, 41, 53]
        ims = [rotate_img(self.image.crop([u, y_min, v, y_max])) for u, v in zip(split_lines[:-1], split_lines[1:])]
        return ims

    def crack(self):
        result = []
        # 加载数据
        with open(os.path.join(current_dir, 'image_data.json'), 'rb') as f:
            image_data = json.load(f)
        for letter in self.handle_split_image():
            letter_vector = build_vector(letter)
            guess = []
            for image in image_data:
                for x, y in image.items():
                    guess.append((distance_hanmming(y, letter_vector), x))
            guess.sort()
            neighbors = guess[:15]  # 距离最近的十五个向量
            class_votes = {}  # 投票
            for neighbor in neighbors:
                class_votes.setdefault(neighbor[-1], 0)
                class_votes[neighbor[-1]] += 1
            sorted_votes = sorted(class_votes.items(), key=lambda x: x[1], reverse=True)
            result.append(sorted_votes[0][0])
        return ''.join(result)

    def __str__(self):
        return self.crack()


if __name__ == "__main__":
    from njupt import Zhengfang

    r = requests.get(Zhengfang.URLs.CAPTCHA)
    im = Image.open(BytesIO(r.content))
    im.show()
    print(ZhengfangCaptcha(im))
