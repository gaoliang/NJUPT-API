# encoding: utf-8

"""
用户认证装饰器(判断用户是否已经登录)
"""

import requests
import requests.utils

from njupt.exceptions import UnauthorizedError
from njupt.urls import URL


def zhengfang_logined(func):
    def wrapper(self, *args, **kwargs):
        if self.verify:  # 利用状态量进行状态的判定
            return func(self, *args, **kwargs)
        else:
            # 先判断有没有cookie文件, 再判断cookie是否有效
            if 'WEB' in requests.utils.dict_from_cookiejar(self.cookies):
                # 判断教务系统是否登录成功，根据正方的一个地址无需参数的地址
                r = self.get_soup(method="get", url=URL.zhengfang_logintest())
                if 'Object moved to ' not in r.text:
                    self.verify = True
                    return func(self, *args, **kwargs)
            raise UnauthorizedError('未登录正方系统，请先登录')

    return wrapper
