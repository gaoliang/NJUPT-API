import time

import requests
from bs4 import BeautifulSoup

from njupt.utils.rsa_encrypt import Encrypt

headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
}


class SSOClient(requests.Session):

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self.headers = headers

    def login(self, username, password):
        login_page_res = self.get('http://202.119.226.235/cas/login')
        login_soup = BeautifulSoup(login_page_res.content, 'lxml')
        execution = login_soup.select_one("#fm1 > input[name=execution]").get('value')
        self.get('http://202.119.226.235/cas/v2/getKaptchaStatus')
        res = self.get('http://202.119.226.235/cas/v2/getPubKey')
        m = res.json()['modulus']
        e = res.json()['exponent']
        pub_key = Encrypt(e=e, m=m)
        password = pub_key.encrypt(password[::-1])
        self.get('http://202.119.226.235/cas/kaptcha?time={}'.format(int(time.time())))
        data = {
            'username': username,
            'password': password,
            'authcode': '',
            'execution': execution,
            '_eventId': 'submit'
        }
        self.post('http://202.119.226.235/cas/login', data=data)
