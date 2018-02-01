import os

import numpy as np
from sklearn.externals import joblib

BLACK = 0
WHITE = 255

current_dir = os.path.dirname(os.path.abspath(__file__))


class ZhengfangCaptcha:
    """
    svm 识别正方验证码
    """
    def __init__(self, im):
        """
        :param im: PIL.image对象
        """
        self.im = im
        self._reduce_noise()

    def _reduce_noise(self):

        # 去除杂色点
        for x in range(self.im.width):
            for y in range(self.im.height):
                pix = self.im.getpixel((x, y))
                # if pix in [43, 85, 128, 170]:
                if pix == 43:
                    # if pix in [43, 85, 86, 127, 128, ]:
                    self.im.putpixel((x, y), WHITE)
                else:
                    self.im.putpixel((x, y), BLACK)

        # 去除单像素噪点并进行二值化(八值法)
        for x in range(self.im.width):
            for y in range(self.im.height):
                count = 0
                if x != 0 and y != 0 and x != self.im.width - 1 and y != self.im.height - 1:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            tx = x + i
                            ty = y + j
                            if self.im.getpixel((tx, ty)) == BLACK:
                                count += 1
                if self.im.getpixel((x, y)) == WHITE and count == 8:
                    self.im.putpixel((x, y), BLACK)

    def handle_split_image(self):
        # 切割验证码，返回包含四个字符图像的列表
        y_min, y_max = 0, 22
        split_lines = [5, 17, 29, 41, 53]
        ims = [self.rotate_img(self.im.crop([u, y_min, v, y_max])) for u, v in zip(split_lines[:-1], split_lines[1:])]
        return ims

    @staticmethod
    def getletter(im):
        # 获取特征值
        all = []
        for x in range(im.width):
            all_t = []
            for y in range(im.height):
                all_t.append(1 if im.getpixel((x, y)) > 0 else 0)
            all += all_t
        return all

    def rotate_img(self, im):
        """
        根据图像在x轴方向投影大小确定字符的摆放方向
        :param im: PIL.Image object
        :return: rotated Image object
        """
        min_count = 1000
        final_angle = 0
        for angle in range(-45, 45):
            x_count = 0
            ti = im.rotate(angle, expand=True)
            for x in range(ti.width):
                for y in range(ti.height):
                    if ti.getpixel((x, y)) == WHITE:
                        x_count += 1
                        break
            if x_count < min_count:
                min_count = x_count
                final_angle = angle
        im = im.rotate(final_angle, expand=False)
        return im

    def _abs_image(self):
        self.im = self.im.cro(self.im.getbbox())

    def crack(self):
        clf = joblib.load(os.path.join(current_dir, 'letter.pkl'))
        temp = []
        for i, img in enumerate(self.handle_split_image()):
            data = self.getletter(img)
            data = np.array([data])
            oneLetter = clf.predict(data)[0]
            temp.append(oneLetter)
        return "".join(temp)

    def __str__(self):
        return self.crack()
