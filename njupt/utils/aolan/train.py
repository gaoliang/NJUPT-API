import os
import pickle

from PIL import Image


# 将图片转换为矢量
def buildvector(im):
    d1 = {}
    count = 0
    for i in im.getdata():
        d1[count] = i
        count += 1
    return d1


if __name__ == "__main__":
    # 字符集
    iconset = ['2', '3', '4', '5', '6', '7', '8', '9']
    # 将图像数据转为向量数据并保存
    imageset = []
    for letter in iconset:
        for img in os.listdir('captcha_chars/{}/'.format(letter)):
            temp = []
            if img != "Thumbs.db" and img != ".DS_Store":
                temp.append(buildvector(Image.open("captcha_chars/{}/{}".format(letter, img))))
            imageset.append({letter: temp})

    with open('imageset.dat', 'wb+') as f:
        pickle.dump(imageset, f)
