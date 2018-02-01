import hashlib
import os
import pickle
import shutil
from PIL import Image

from njupt.utils import ZhengfangCaptcha

BLACK = 0
WHITE = 255
import time


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


if __name__ == "__main__":
    # spilt2chars()
    iconset = list('qwertyuiopasdfghjklzcxvbnm1234567890')
    # 将图像数据转为向量数据并保存
    imageset = []
    for letter in iconset:
        try:
            for img in os.listdir('captcha_chars/{}/'.format(letter)):
                temp = []
                if img != "Thumbs.db" and img != ".DS_Store":
                    temp.append(ZhengfangCaptcha.buildvector(Image.open("captcha_chars/{}/{}".format(letter, img))))
                    print(temp)

                imageset.append({letter: temp})
        except:
            print(letter)

    with open('imageset.dat', 'wb+') as f:
        pickle.dump(imageset, f)
