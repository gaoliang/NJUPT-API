# encoding: utf-8
import hashlib

from njupt import settings
from njupt.models.base import Model
from njupt.urls import URL


class JwxtAccount(Model):
    def login(self, account, password):
        """
        登录教务系统 jwxt.njupt.edu.cn
        :param account: 南邮学号
        :param password: 密码
        :return: {'r': 1, "msg": "登录失败"} 或 {'r': 0, 'msg': '登录成功'}
        """
        data = {
            "__VIEWSTATE": self._get_viewstate(),
            'txtUserName': account,
            'TextBox2': password,
            'RadioButtonList1': "%D1%A7%C9%FA",
            "txtSecretCode": self._get_captcha(URL.jwxt_captcha()),
            "Button1": "",
            "hidPdrs": "",
            "hidsc": ""
        }
        return self._login_execute(url=URL.jwxt_login(), data=data)

    def _login_execute(self, url=None, data=None):
        r = self._execute(method="post", url=url, data=data)
        if r.ok:
            if "请到信息维护中完善个人联系方式" in r.text:
                self.cookies.save(ignore_discard=True)  # 保存登录信息cookies
                self.cookies.load(filename=settings.COOKIES_FILE, ignore_discard=True)
                return {'r': 0, 'msg': '登录成功'}
            else:
                return {'r': 1, 'msg': '检查账号密码验证码是否正确'}
        else:
            return {'r': 1, "msg": "登录失败"}


class AolanAccount(Model):
    def login(self, account, password):
        """
        登录奥兰系统 jwxt.njupt.edu.cn
        :param account: 南邮学号、考生号、身份证号
        :param password: 密码
        :return: {'r': 1, "msg": "登录失败"} 或 {'r': 0, 'msg': '登录成功'}
        """
        data = {
            "__VIEWSTATE": self._get_viewstate(URL.aolan_login()),
            '__VIEWSTATEGENERATOR': self._get_viewstategenerator(URL.aolan_login()),
            'userbh': account,
            'pas2s': hashlib.md5(password.upper().encode('utf8')).hexdigest(),
            "vcode": self._get_captcha(URL.aolan_captcha()),
            "cw": "",
            "xzbz": "1",
        }
        return self._login_execute(url=URL.aolan_login(), data=data)

    def _login_execute(self, url=None, data=None):
        r = self._execute(method="post", url=url, data=data)
        if r.ok:
            if "辅导员评议" in r.text:
                self.cookies.save(ignore_discard=True)  # 保存登录信息cookies
                self.cookies.load(filename=settings.COOKIES_FILE, ignore_discard=True)
                return {'r': 0, 'msg': '登录成功'}
            else:
                return {'r': 1, 'msg': '检查账号密码验证码是否正确'}
        else:
            return {'r': 1, "msg": "登录失败"}


class LibAccount(Model):
    def login(self, account, password):
        """
        登录南邮图书馆 jwxt.njupt.edu.cn
        :param account: 南邮学号
        :param password: 密码
        :return: {'r': 1, "msg": "登录失败"} 或 {'r': 0, 'msg': '登录成功'}
        """
        data = {
            "number": account,
            'passwd': password,
            'captcha': self._get_captcha(URL.lib_captcha()),
            'select': "cert_no",
            "returnUrl": "",
        }
        return self._login_execute(url=URL.jwxt_login(), data=data)

    def _login_execute(self, url=None, data=None):
        r = self._execute(method="post", url=url, data=data)
        if r.ok:
            print(r.text)
            if "请到信息维护中完善个人联系方式" in r.text:
                self.cookies.save(ignore_discard=True)  # 保存登录信息cookies
                self.cookies.load(filename=settings.COOKIES_FILE, ignore_discard=True)
                return {'r': 0, 'msg': '登录成功'}
            else:
                return {'r': 1, 'msg': '检查账号密码验证码是否正确'}
        else:
            return {'r': 1, "msg": "登录失败"}
