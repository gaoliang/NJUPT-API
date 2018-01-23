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

from njupt.utils import AolanCaptcha, ZhengfangCaptcha

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
        self.headers['Referer'] = url
        soup = self._url2soup('get', url)
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
            return str(AolanCaptcha(im))
        if url == URL.jwxt_captcha():
            return str(ZhengfangCaptcha(im))

    def _url2soup(self, method="post", url=None, params=None, json=None, data=None, **kwargs):
        """
        通用请求方法
        :param method: 请求方法
        :param url:     请求URL
        :param params:  请求参数
        :param data:    请求数据
        :param data_type:    提交的数据格式(可能是表单类型,也可能是json格式的字符串)
        :param kwargs:  requests支持的参数，比如可以设置代理参数
        :return: BeautifulSoup对象
        """
        # r = getattr(self, method)(url, json=json, data=data, params=params, **kwargs)
        # if r.ok:
        #     soup = BeautifulSoup(r.text, 'lxml')
        #     return soup
        # else:
        #     raise ConnectionError("检查网络连接")

        try:  # 出现网络连接问题,直接在该处抛出错误
            r = getattr(self, method)(url, json=json, data=data, params=params, **kwargs)
        except ConnectionError:
            raise ConnectionError("请检查网络连接")
        else:
            if r.ok:  # 状态码小于400为True
                soup = BeautifulSoup(r.text, 'lxml')
                return soup
            else:  # 处理其他状态码
                raise Exception('请确保能够正常访问当前页面: {}'.format(url))


if __name__ == "__main__":
    test_model = Model()
    test_model._get_captcha(URL.aolan_captcha())
