"""
奥兰系统验证码识别
"""
import os
import pickle
import requests
import math

from njupt.settings import BASE_DIR
from njupt.urls import URL
from PIL import Image
from io import BytesIO

# 对图像进行纵向分割的分割点
letters = [(3, 11), (23, 31), (43, 51), (63, 71)]


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


def crack_aolan_captcha(im):
    """
    :param im: 需要识别的图像文件，路径或PIL.Image对象
    :return: 识别结果
    """
    # 路径或BytesIO或文件时
    if isinstance(im, str) or isinstance(im, BytesIO) or type(im) == "file":
        im = Image.open(im)

    # 灰度处理
    imgry = im.convert('L')

    # 二值处理
    threshold = 220
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    out = imgry.point(table, '1')
    v = VectorCompare()
    # 装载训练数据集
    with open(os.path.join(BASE_DIR, 'utils', 'datas', 'imageset.dat'), 'rb+') as f:
        imageset = pickle.load(f)
    # 对验证码图片进行切割
    result = []
    for letter in letters:
        final = out.crop((letter[0], 0, letter[1], out.size[1]))
        guess = []
        # 将切割得到的验证码小片段与每个训练片段进行比较
        for image in imageset:
            for x, y in image.items():
                if len(y) != 0:
                    guess.append((v.relation(y[0], buildvector(final)), x))
        guess.sort(reverse=True)
        print(guess[0])
        result.append(guess[0][1])
    return "".join(result)


if __name__ == "__main__":
    r = requests.get(URL.aolan_captcha())
    im = Image.open(BytesIO(r.content))
    print(crack_aolan_captcha(im))
