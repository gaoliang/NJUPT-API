import time

from njupt import Zhengfang
from njupt.base import APIWrapper
from njupt.utils.rsa_encrypt import encrypt


class SSO(APIWrapper):
    """
    my.njupt.edu.cn 统一认证系统的封装，在这里可以实现无验证码跳转到教务系统， 一卡通系统(限内网)

    :param username: 学生登录账号为学号，教工登录账号为8位工号。
    :param password: 智慧校园密码，没修改过的为初始密码（身份证号码后六位）。

    >>> from njupt import SSO
    >>> sso = SSO('B12345678', 'abcedhgh')
    >>> zf = sso.zhengfang()
    """

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self._login()

    def _login(self):
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
