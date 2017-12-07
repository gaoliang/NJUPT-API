"""
奥兰系统验证码识别，利用向量空间余弦相似度实现
"""
import os
import pickle
import requests
import math
from njupt.urls import URL
from PIL import Image
from io import BytesIO

# 对图像进行纵向分割的分割点

letters = [(3, 11), (23, 31), (43, 51), (63, 71)]
current_dir = os.path.dirname(os.path.abspath(__file__))


class VectorCompare:
    # 计算矢量大小
    def magnitude(self, concordance):
        total = 0
        for word, count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    # 计算矢量之间的 cos 值
    def relation(self, concordance1, concordance2):
        relevance = 0
        topvalue = 0
        for word, count in concordance1.items():
            if word in concordance2:
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))


# 将图片转换为矢量
def buildvector(im):
    d1 = {}
    count = 0
    for i in im.getdata():
        d1[count] = i
        count += 1
    return d1


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
                table.append(0)
            else:
                table.append(1)
        self.im = self.im.point(table, '1')

    def crack(self):
        v = VectorCompare()
        # 装载训练数据集
        with open(os.path.join(current_dir, 'imageset.dat'), 'rb+') as f:
            imageset = pickle.load(f)
        # 对验证码图片进行切割
        result = []
        for letter in letters:
            final = self.im.crop((letter[0], 0, letter[1], self.im.size[1]))
            guess = []
            # 将切割得到的验证码小片段与每个训练片段进行比较
            for image in imageset:
                for x, y in image.items():
                    if len(y) != 0:
                        guess.append((v.relation(y[0], buildvector(final)), x))
            guess.sort(reverse=True)
            result.append(guess[0][1])
        return "".join(result)

    def __str__(self):
        return self.crack()


if __name__ == "__main__":
    r = requests.get(URL.aolan_captcha())
    im = Image.open(BytesIO(r.content))
    print(AolanCaptcha(im))
