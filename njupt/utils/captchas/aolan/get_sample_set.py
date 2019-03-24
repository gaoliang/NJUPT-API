"""
手动获取奥兰系统验证码的数据集
"""
import hashlib
import time
from io import BytesIO

import requests
from PIL import Image

from njupt.urls import URL
from njupt.utils.captchas.aolan.aolan_captcha import letters

for i in range(100):
    r = requests.get(URL.aolan_captcha())
    im = Image.open(BytesIO(r.content))
    # 灰度处理
    imgry = im.convert('L')
    # 二值处理
    threshold = 220
    table = []
    for i in range(256):
        table.append(0 if i < threshold else 1)
    out = imgry.point(table, '1')
    out.show()
    numbers = input("输入数值")
    if numbers == "-1":
        continue
    count = 0
    for letter, value in zip(letters, numbers):
        m = hashlib.md5()
        m.update("{}{}".format(time.time(), count).encode('utf8'))
        temp = out.crop((letter[0], 0, letter[1], out.size[1]))
        temp.save('captcha_chars/{}/{}.png'.format(value, m.hexdigest()))
        count += 1
