# encoding: utf-8
from io import BytesIO

import requests
import urllib3
from PIL import Image
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class API(requests.Session):
    def __init__(self):
        super(API, self).__init__()
        self.verify = False

    def _get_viewstate(self, url=None):
        self.headers['Referer'] = url
        soup = self.get_soup(url=url)
        viewstate = soup.find('input', attrs={"name": "__VIEWSTATE"}).get("value")
        return viewstate

    def _get_viewstategenerator(self, url=None):
        response = self.get(url or url.aolan_login())
        soup = BeautifulSoup(response.content, "lxml")
        viewstate = soup.find('input', attrs={"name": "__VIEWSTATEGENERATOR"}).get("value")
        return viewstate

    def get_image(self, url=None, method="get", params=None, json=None, data=None, **kwargs):
        """
        图片接口通用请求方法
        :param method: 请求方法，默认为get
        :param url:     请求URL
        :param params:  请求参数
        :param data:    请求数据
        :param kwargs:  requests支持的参数，比如可以设置代理参数
        :return: pillow的Image对象
        """
        try:  # 出现网络连接问题,直接在该处抛出错误
            r = getattr(self, method)(url, json=json, data=data, params=params, **kwargs)
            return Image.open(BytesIO(r.content))
        except ConnectionError:
            raise ConnectionError("请检查网络连接")

    def get_soup(self, url=None, method="get", params=None, json=None, data=None, **kwargs):
        """
        html页面通用请求方法
        :param method: 请求方法，默认为get
        :param url:     请求URL
        :param params:  请求参数
        :param data:    请求数据
        :param kwargs:  requests支持的参数，比如可以设置代理参数
        :return: BeautifulSoup对象
        """
        try:  # 出现网络连接问题,直接在该处抛出错误
            r = getattr(self, method)(url, json=json, data=data, params=params, **kwargs)
        except ConnectionError:
            raise ConnectionError("请检查网络连接")
        else:
            if r.ok:  # 状态码小于400为True
                soup = BeautifulSoup(r.content, 'lxml')
                return soup
            else:  # 处理其他状态码
                raise Exception('请确保能够正常访问当前页面: {}'.format(url))

    def get_json(self, url=None, method="get", params=None, json=None, data=None, **kwargs):
        """
        json接口通用请求方法
        :param method: 请求方法, 默认为get
        :param url:     请求URL
        :param params:  请求参数
        :param data:    请求数据
        :param kwargs:  requests支持的参数，比如可以设置代理参数
        :return: json转换出的字典
        """
        try:  # 出现网络连接问题,直接在该处抛出错误
            r = getattr(self, method)(url, json=json, data=data, params=params, **kwargs)
            return r.json()
        except ConnectionError:
            raise ConnectionError("请检查网络连接")
