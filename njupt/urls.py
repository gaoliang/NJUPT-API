# encoding: utf-8
"""
通用ＵＲＬ类,NJUPT各个网站的ＵＲＬ接口地址
"""


class URL(object):
    host = "https://www.njupt.edu.cn"
    jwxt_host = "http://jwxt.njupt.edu.cn"
    aolan_host = "http://stu.njupt.edu.cn"
    lib_host = "http://202.119.228.6:8080"

    @classmethod
    def jwxt_logintest(cls):
        return cls.jwxt_host + '/content.aspx'

    @classmethod
    def jwxt_grade(cls, account):
        return cls.jwxt_host + '/xscj_gc.aspx?xh={}&xm=%B8%DF%C1%C1&gnmkdm=N121605'.format(account)

    @classmethod
    def jwxt_class_schedule(cls, account):
        return cls.jwxt_host + '/xskbcx.aspx?xh={}&xm=%B8%DF%C1%C1&gnmkdm=N121603'.format(account)

    @classmethod
    def jwxt_captcha(cls):
        # 教务系统验证码
        return cls.jwxt_host + '/CheckCode.aspx'

    @classmethod
    def jwxt_login(cls):
        # 教务系统登录
        return cls.jwxt_host + '/default2.aspx'

    @classmethod
    def aolan_captcha(cls):
        return cls.aolan_host + '/VCode.aspx'

    @classmethod
    def aolan_login(cls):
        # 奥兰系统登录
        return cls.aolan_host + "/LOGIN.ASPX"

    @classmethod
    def lib_login(cls):
        # 图书馆登录
        return cls.lib_host + '/reader/redr_verify.php'

    @classmethod
    def lib_captcha(cls):
        # 图书馆验证码
        return cls.lib_host + '/reader/captcha.php'
