# encoding: utf-8

"""
用户认证装饰器(判断用户是否已经登录)
"""

import requests
import requests.utils
from njupt.urls import URL


# def zhengfang_logined(func):
#     def wrapper(self, *args, **kwargs):
#         success = False
#         # 先判断有没有cookie文件, 再判断cookie是否有效
#         if 'WEB' in requests.utils.dict_from_cookiejar(self.cookies):
#             # 判断教务系统是否登录成功，根据正方的一个地址无需参数的地址
#             r = self._url2soup(method="get", url=URL.jwxt_logintest())
#             if 'Object moved to ' not in r.text:
#                 success = True
#         while not success:
#             account = input("请输入教务系统账号:")
#             self.account = account
#             password = input("请输入账号密码:")
#             data = self.login(account, password)
#             if data.get("r") == 0:
#                 success = True
#             else:
#                 print(data.get("msg"))
#         else:
#             return func(self, *args, **kwargs)
#     return wrapper


def zhengfang_logined(func):
    def wrapper(self, *args, **kwargs):
        if self.verify:  # 利用状态量进行状态的判定
            return func(self, *args, **kwargs)
        else:
            # 先判断有没有cookie文件, 再判断cookie是否有效
            if 'WEB' in requests.utils.dict_from_cookiejar(self.cookies):
                # 判断教务系统是否登录成功，根据正方的一个地址无需参数的地址
                r = self._url2soup(method="get", url=URL.zhengfang_logintest())
                if 'Object moved to ' not in r.text:
                    self.verify = True
                    return func(self, *args, **kwargs)
            while True:  # 运行到此处代表cookies无效
                data = self.login(self.account, input('输入密码:'))
                if data.get('r') == 0:
                    self.verify = True
                    return func(self, *args, **kwargs)
                else:
                    print(data.get('msg'))

    return wrapper
