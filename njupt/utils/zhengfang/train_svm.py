import hashlib
import os
import shutil

from PIL import Image
from sklearn.externals import joblib
from sklearn.svm import SVC

BLACK = 0
WHITE = 255
import time

from .zhengfang_captcha import ZhengfangCaptcha


def spilt2chars():
    """
    分割已有的数据为字符并保存
    """
    try:
        shutil.rmtree('captcha_chars')
    except:
        pass
    os.mkdir("captcha_chars")
    values = "abcdefghijklmnopqrstuvwxyz1234567890"
    for value in values:
        os.mkdir('captcha_chars/{}'.format(value))

    file_names = os.listdir('captchas')
    for file_name in file_names:  #
        if not os.path.isdir(file_name) and file_name != '.DS_Store':
            values = file_name[:4]
            im = Image.open('captchas/{}'.format(file_name))
            captcha = ZhengfangCaptcha(im)
            for im_part, value in zip(captcha.handle_split_image(), values):
                m = hashlib.md5()
                m.update("{}{}".format(time.time(), value).encode('utf8'))
                im_part.save("captcha_chars/{}/{}.png".format(value, m.hexdigest()))


def buildvector(im):
    d1 = {}
    count = 0
    for i in im.getdata():
        d1[count] = i
        count += 1
    return d1


# 提取字母的svm特征值
def getletter(im):
    all = []
    for x in range(im.width):
        all_t = []
        for y in range(im.height):
            all_t.append(1 if im.getpixel((x, y)) > 0 else 0)
        all += all_t
    return all


# 提取特征值
def extractLetters(path):
    """
    :param path: 存放已经分割好的字符文件夹的父目录路径
    :return: 提取的特征值
    """
    x = []
    y = []
    # 遍历文件夹 获取下面的目录
    for root, sub_dirs, files in os.walk(path):
        for dir in sub_dirs:
            # 获得每个文件夹的图片
            for fileName in os.listdir(path + '/' + dir):
                print(dir, fileName)
                if fileName != "Thumbs.db" and fileName != ".DS_Store":
                    # 打开图片
                    x.append(getletter(Image.open(path + '/' + dir + '/' + fileName)))
                    y.append(dir)
    print(x)
    return x, y


# svm训练
def trainSVM():
    array = extractLetters('captcha_chars')
    # 使用向量机SVM进行机器学习
    letterSVM = SVC(kernel="linear", C=1, probability=True).fit(array[0], array[1])
    # 生成训练结果
    joblib.dump(letterSVM, 'letter.pkl')


if __name__ == "__main__":
    spilt2chars()
    trainSVM()
