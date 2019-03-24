import json
import os

from PIL import Image

from njupt.utils.captchas import distance_hanmming, build_vector

BLACK = 0
WHITE = 255

current_dir = os.path.dirname(os.path.abspath(__file__))


class CardCaptcha:
    """
    一卡通系统的验证码工具类
    """

    def __init__(self, im):
        """
        :param im: PIL.image对象
        """
        self.im = im.convert('L')
        self.image_pre_process()

    def image_pre_process(self):

        threshold = 200
        # 去除杂色点
        for x in range(self.im.width):
            for y in range(self.im.height):
                pix = self.im.getpixel((x, y))
                if pix > threshold:
                    self.im.putpixel((x, y), BLACK)
                else:
                    self.im.putpixel((x, y), WHITE)

    def handle_split_image(self):
        # 切割验证码，返回包含五个字符图像的列表
        y_min, y_max = 0, 82
        split_lines = [7, 49, 91, 133, 175, 217]
        ims = [self.im.crop([u, y_min, v, y_max]) for u, v in zip(split_lines[:-1], split_lines[1:])]
        return ims

    def crack(self):
        result = []
        # 装载训练数据集
        with open(os.path.join(current_dir, 'image_data.json'), 'rb') as f:
            image_data = json.load(f)
        for letter in self.handle_split_image():
            letter_vector = build_vector(letter)
            guess = []
            for image in image_data:
                for x, y in image.items():
                    if len(y) != 0:
                        guess.append((distance_hanmming(y, letter_vector), x))
            guess.sort()
            result.append(guess[0][1])
        return ''.join(result)

    def __str__(self):
        return self.crack()


if __name__ == "__main__":
    im = Image.open("captchas/12272.gif")
    im.show()
    print(CardCaptcha(im).crack())
