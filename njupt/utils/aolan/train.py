import os
import pickle

from PIL import Image

# 将图片转换为矢量
from njupt.settings import BASE_DIR


def buildvector(im):
    d1 = {}
    count = 0
    for i in im.getdata():
        d1[count] = i
        count += 1
    return d1


# 字符集
iconset = ['2', '3', '4', '5', '6', '7', '8', '9']

# 训练
imageset = []
for letter in iconset:
    for img in os.listdir(os.path.join(BASE_DIR, 'utils', 'datas', 'sample_set/{}/'.format(letter))):
        temp = []
        if img != "Thumbs.db" and img != ".DS_Store":
            temp.append(
                buildvector(
                    Image.open(os.path.join(BASE_DIR, 'utils', 'datas', "sample_set/{}/{}".format(letter, img)))))
        imageset.append({letter: temp})

with open(os.path.join(BASE_DIR, 'utils', 'datas', 'imageset.dat'), 'wb+') as f:
    pickle.dump(imageset, f)
