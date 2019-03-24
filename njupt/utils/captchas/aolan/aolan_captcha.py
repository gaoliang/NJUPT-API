"""
奥兰系统验证码识别，利用向量空间余弦相似度实现
"""
import os
import pickle
from io import BytesIO

from PIL import Image

# 对图像进行纵向分割的分割点
from njupt.utils.captchas import distance_cos, build_vector

letters = [(3, 11), (23, 31), (43, 51), (63, 71)]
current_dir = os.path.dirname(os.path.abspath(__file__))

BLACK = 0
WHITE = 255


class AolanCaptcha:
    # 分割点
    letters = [(3, 11), (23, 31), (43, 51), (63, 71)]

    def __init__(self, im):
        # 路径或BytesIO或文件时
        if isinstance(im, str) or isinstance(im, BytesIO) or type(im) == "file":
            self.im = Image.open(im)
        elif isinstance(im, Image.Image):
            self.im = im
        else:
            raise TypeError("错误的类型")
        self.binarize()

    def binarize(self):
        # 灰度处理
        self.im = self.im.convert('L')

        # 二值处理
        threshold = 220
        table = []
        for i in range(256):
            if i < threshold:
                table.append(BLACK)
            else:
                table.append(WHITE)
        self.im = self.im.convert('1')

    def crack(self):
        # 装载训练数据集
        with open(os.path.join(current_dir, 'imageset.dat'), 'rb') as f:
            imageset = pickle.load(f)
        # 对验证码图片进行切割
        result = []
        for letter in letters:
            final = self.im.crop((letter[0], 0, letter[1], self.im.size[1]))
            letter_vector = build_vector(final)
            guess = []
            # 将切割得到的验证码小片段与每个训练片段进行比较
            for image in imageset:
                for x, y in image.items():
                    guess.append((distance_cos(y, letter_vector), x))
            guess.sort()
            result.append(guess[0][1])
        return "".join(result)

    def __str__(self):
        return self.crack()