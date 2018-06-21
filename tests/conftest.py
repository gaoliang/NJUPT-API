import os
import re
from functools import wraps

import pytest
import responses

from njupt import Card, Zhengfang


@pytest.fixture(scope='session')
def card():
    card = Card()
    card.account = 'account'
    card.verify = True
    return card


@pytest.fixture(scope='session')
def zhengfang():
    zhengfang = Zhengfang()
    zhengfang.account = 'account'
    zhengfang.verify = True
    return zhengfang


ALL_URL_RE = re.compile('.*')
TEST_DIR = os.path.dirname(os.path.abspath(__file__))


def mock_response(method='GET', url=ALL_URL_RE, body=None, file_name=None, json=None, status=200):
    """
    mock requests请求的装饰器， 方便写测试用
    :param method: 请求方法, 可选'GET', 'POST'等
    :type body: bytes or str
    :param body: response的响应体， bytes
    :param url: 需要进行mock的请求地址， 默认为mock全部地址
    :param file_name: 如果需要设置response的body为文件内容，则传入相对于tests根目录的路径
    :param json: json字符串，用于response.json()
    :param status: HTTP状态码
    """
    if file_name:
        body = open(os.path.join(TEST_DIR, file_name), 'r').read().encode('gb2312')

    def _mock_reponse(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            responses.add(method=method,
                          url=url,
                          json=json,
                          body=body,
                          status=status
                          )
            result = func(*args, **kwargs)
            responses.remove(method, url)
            return result

        return wrapper

    return _mock_reponse
