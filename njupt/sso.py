import time

from njupt import Zhengfang, Card
from njupt.base import APIWrapper
from njupt.utils.rsa_encrypt import encrypt


class SSO(APIWrapper):

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self.login()

    def login(self):
        login_soup = self.get_soup('http://202.119.226.235/cas/login')
        execution = login_soup.select_one("#fm1 > input[name=execution]").get('value')
        self.get('http://202.119.226.235/cas/v2/getKaptchaStatus')
        res = self.get_json('http://202.119.226.235/cas/v2/getPubKey')
        encrypted_password = encrypt(
            e=res['exponent'],
            m=res['modulus'],
            message=self.password[::-1]
        )
        self.get('http://202.119.226.235/cas/kaptcha?time={}'.format(int(time.time())))
        data = {
            'username': self.username,
            'password': encrypted_password,
            'authcode': '',
            'execution': execution,
            '_eventId': 'submit'
        }
        self.post('http://202.119.226.235/cas/login', data=data)

    def zhengfang(self):
        return Zhengfang(sso_session=self)
