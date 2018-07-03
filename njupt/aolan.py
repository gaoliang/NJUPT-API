import hashlib

from njupt.base import Model
from njupt.urls import URL
from njupt.utils import AolanCaptcha


class Aolan(Model):
    def login(self, account, password):
        """
        登录奥兰系统 jwxt.njupt.edu.cn
        :param account: 南邮学号、考生号、身份证号
        :param password: 密码
        :return: {'r': 1, "msg": "登录失败"} 或 {'r': 0, 'msg': '登录成功'}
        """
        captcha_code = AolanCaptcha(self.get_image(URL.aolan_captcha())).crack()
        data = {
            "__VIEWSTATE": self._get_viewstate(URL.aolan_login()),
            '__VIEWSTATEGENERATOR': captcha_code,
            'userbh': account,
            'pas2s': hashlib.md5(password.upper().encode('utf8')).hexdigest(),
            "vcode": (URL.aolan_captcha()),
            "cw": "",
            "xzbz": "1",
        }
        return self._login_execute(url=URL.aolan_login(), data=data)

    def _login_execute(self, url=None, data=None):
        r = self.post(url=url, data=data)
        if r.ok:
            if "辅导员评议" in r.text:
                self.cookies.save(ignore_discard=True)  # 保存登录信息cookies
                return {'r': 0, 'msg': '登录成功'}
            else:
                return {'r': 1, 'msg': '检查账号密码验证码是否正确'}
        else:
            return {'r': 1, "msg": "登录失败"}
