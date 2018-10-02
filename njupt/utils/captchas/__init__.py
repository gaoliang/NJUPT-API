import math
import operator
from functools import reduce

BLACK = 0
WHITE = 255


def magnitude(concordance):
    total = reduce(operator.add, map(lambda x: x ** 2, concordance))
    return math.sqrt(total)


# 计算矢量之间的余弦距离
def distance_cos(vector1, vector2):
    sum_value = 0
    for value1, value2 in zip(vector1, vector2):
        sum_value += value1 * value2
    return 1 - sum_value / (magnitude(vector1) * magnitude(vector2))


def distance_hanmming(vector1, vector2):
    """
    计算两向量的汉明距，（向量只包含0，1时）
    """
    count = 0
    for value1, value2 in zip(vector1, vector2):
        if value1 != value2:
            count += 1
    return count


def build_vector(image, binary=True):
    """
    图像转一维特征向量
    :param image: pillow Image object with mode 1 or mode L
    :param binary: 黑白图是否生成为0，1向量
    :return: list of int
    """
    vector = []
    for pixel in image.getdata():
        if binary:
            vector.append(1 if pixel == 255 else 0)
        else:
            vector.append(pixel)
    return vector


def rotate_img(image):
    """
    根据图像在x轴方向投影大小确定字符的摆放方向
    :param image: PIL.Image object
    :return: rotated Image object
    """
    min_count = 1000
    final_angle = 0
    for angle in range(-45, 45):
        x_count = 0
        ti = image.rotate(angle, expand=True)
        for x in range(ti.width):
            for y in range(ti.height):
                if ti.getpixel((x, y)) == WHITE:
                    x_count += 1
                    break
        if x_count < min_count:
            min_count = x_count
            final_angle = angle
    image = image.rotate(final_angle, expand=False)
    return image
