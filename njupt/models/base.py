# encoding: utf-8

"""

NJUPT-API的抽象基类，任何对象都可以继承

"""
from io import BytesIO

import requests
import urllib3
from bs4 import BeautifulSoup
from http import cookiejar
from njupt import settings
from njupt.urls import URL
from PIL import Image

from njupt.utils.aolan.aolan_captcha import crack_aolan_captcha

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Model(requests.Session):
    def __init__(self):
        super(Model, self).__init__()
        self.cookies = cookiejar.LWPCookieJar(filename=settings.COOKIES_FILE)
        try:
            self.cookies.load(ignore_discard=True)
        except FileNotFoundError:
            pass
        self.verify = False
        self.headers = settings.HEADERS

    def _get_viewstate(self, url=None):
        response = self.get(url or URL.jwxt_login())
        soup = BeautifulSoup(response.content, "lxml")
        viewstate = soup.find('input', attrs={"name": "__VIEWSTATE"}).get("value")
        return viewstate

    def _get_viewstategenerator(self, url=None):
        response = self.get(url or url.aolan_login())
        soup = BeautifulSoup(response.content, "lxml")
        viewstate = soup.find('input', attrs={"name": "__VIEWSTATEGENERATOR"}).get("value")
        return viewstate

    def _get_captcha(self, url=URL.jwxt_captcha()):
        r = self.get(url)
        im = Image.open(BytesIO(r.content))
        if url == URL.aolan_captcha():
            return crack_aolan_captcha(im)
        im.show()
        captcha = input("输入验证码：")
        return captcha

    def _execute(self, method="post", url=None, params=None, json=None, data=None, **kwargs):
        """
        通用请求方法
        :param method: 请求方法
        :param url:     请求URL
        :param params:  请求参数
        :param data:    请求数据
        :param data_type:    提交的数据格式(可能是表单类型,也可能是json格式的字符串)
        :param kwargs:  requests支持的参数，比如可以设置代理参数
        :return: response
        """
        r = getattr(self, method)(url, json=json, data=data, params=params, **kwargs)
        return r


if __name__ == "__main__":
    test_model = Model()
    test_model._get_captcha(URL.aolan_captcha())
