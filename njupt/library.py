from enum import Enum

from njupt.base import API
from njupt.exceptions import AuthenticationException
from njupt.utils import login_required
from njupt.utils.captchas.library.libray_captcha import LibraryCaptcha


class LoginType(Enum):
    """
    图书馆的登录方式

    - STUDENT_ID: 学号
    - CARD_ID: 一卡通号
    - EMAIL: 邮箱
    """
    STUDENT_ID = 'cert_no'
    CARD_ID = 'bar_no'
    EMAIL = 'email'


class Library(API):
    """图书馆

    :param username: 用户名
    :param password: 密码
    :param login_type:  :class:`LoginType`, 默认为一卡通账号
    """

    class URLs:
        HOST = "http://202.119.228.6:8080"
        # 验证码
        CAPTCHA = HOST + '/reader/captcha.php?0.2226025362345463'
        # 登录
        LOGIN = HOST + '/reader/redr_verify.php'
        # 信息
        INFO = HOST + '/reader/redr_info_rule.php'

    def __init__(self, username, password, login_type=LoginType.CARD_ID):
        super().__init__()
        self.username = username
        self.password = password
        if self.username and self.password:
            self.login(username, password, login_type)

    def login(self, username, password, login_type):
        captcha_code = str(LibraryCaptcha(self.get_image(self.URLs.CAPTCHA)))
        data = {
            'number': username,
            'passwd': password,
            'captcha': captcha_code,
            'select': login_type.value,
            'returnUrl': ''
        }
        res = self.post(url=self.URLs.LOGIN, data=data)
        res.encoding = 'utf-8'
        if '注销' in res.text:
            self.verify = True
        else:
            raise AuthenticationException('incorrect username or password')

    @login_required
    def get_info(self):
        """基本信息

        :return: dict of user info
        :rtype: dict

        >>> library.get_info()
        {
            '姓名': '张三',
            '证件号': 'B12345678',
            '条码号': '11020151234556,
            '最大可借图书': '23',
            ...
        }
        """
        soup = self.get_soup(self.URLs.INFO)
        table = soup.select_one('#mylib_info > table')
        info = {}
        for tr in table.select('tr'):
            for td in tr.select('td'):
                text = td.text.strip()
                if not text:
                    continue
                key, value = text.split('：')
                info[key.strip()] = value.strip()
        return info


if __name__ == "__main__":
    lib = Library('110201500467700', '12')
    print(lib.get_info())
