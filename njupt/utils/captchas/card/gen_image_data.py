import hashlib
import json
import os
import shutil
import time

from PIL import Image

from njupt.utils.captchas import build_vector
from njupt.utils.captchas.card import CardCaptcha

BLACK = 0
WHITE = 255


def spilt2chars():
    """
    分割已有的数据为字符并保存
    """
    try:
        shutil.rmtree('captcha_chars')
    except FileNotFoundError:
        pass
    os.mkdir("captcha_chars")
    values = "1234567890"
    for value in values:
        os.mkdir('captcha_chars/{}'.format(value))

    file_names = os.listdir('captchas')
    for file_name in file_names:  #
        if not os.path.isdir('captchas/{}'.format(file_name)) and file_name != '.DS_Store':
            values = file_name[:4]
            im = Image.open('captchas/{}'.format(file_name))
            captcha = CardCaptcha(im)
            for im_part, value in zip(captcha.handle_split_image(), values):
                m = hashlib.md5()
                m.update("{}{}".format(time.time(), value).encode('utf8'))
                im_part.save("captcha_chars/{}/{}.png".format(value, m.hexdigest()))


if __name__ == "__main__":
    # spilt2chars()
    iconset = list('0123456789')
    # # 将图像数据转为向量数据并保存
    image_data = []
    for letter in iconset:
        try:
            for img in os.listdir('captcha_chars/{}/'.format(letter)):
                if img != "Thumbs.db" and img != ".DS_Store":
                    temp = build_vector(Image.open("captcha_chars/{}/{}".format(letter, img)))
                    image_data.append({letter: temp})
        except FileNotFoundError:
            print(letter)

    with open('image_data.json', 'w') as f:
        json.dump(image_data, f)
