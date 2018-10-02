import os
import json

from PIL import Image

from njupt.utils.captchas import build_vector

if __name__ == "__main__":
    # 字符集
    letters = ['2', '3', '4', '5', '6', '7', '8', '9']
    # 将图像数据转为向量数据并保存
    image_data = []
    for letter in letters:
        for img in os.listdir('captcha_chars/{}/'.format(letter)):
            if img != "Thumbs.db" and img != ".DS_Store":
                temp = build_vector(Image.open("captcha_chars/{}/{}".format(letter, img)))
                image_data.append({letter: temp})

    with open('image_data.json', 'w') as f:
        json.dump(image_data, f)
