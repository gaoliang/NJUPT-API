# encoding: utf-8
"""
通用ＵＲＬ类,NJUPT各个网站的ＵＲＬ接口地址
"""


class URL(object):
    HOST = "https://www.njupt.edu.cn"
    ZHENGFANG_HOST = "http://jwxt.njupt.edu.cn"
    AOLAN_HOST = "http://stu.njupt.edu.cn"
    LIB_HOST = "http://202.119.228.6:8080"
    CARD_HOST = "http://yktapp.njupt.edu.cn:8070"

    @classmethod
    def zhengfang_logintest(cls):
        return cls.ZHENGFANG_HOST + '/content.aspx'

    @classmethod
    def zhengfang_score(cls, account):
        return cls.ZHENGFANG_HOST + '/xscj_gc.aspx?xh={}&xm=%B8%DF%C1%C1&gnmkdm=N121605'.format(account)

    @classmethod
    def zhengfang_class_schedule(cls, account):
        return cls.ZHENGFANG_HOST + '/xskbcx.aspx?xh={}&xm=%B8%DF%C1%C1&gnmkdm=N121603'.format(account)

    @classmethod
    def zhengfang_grade(cls, account):
        return cls.ZHENGFANG_HOST + '/xsdjkscx.aspx?xh={}&xm=%B8%DF%C1%C1&gnmkdm=N121606'.format(account)

    @classmethod
    def zhengfang_courses(cls, account):
        return cls.ZHENGFANG_HOST + '/xsxkqk.aspx?xh={}&xm=%B8%DF%C1%C1&gnmkdm=N121615'.format(account)

    @classmethod
    def zhengfang_captcha(cls):
        # 教务系统验证码
        return cls.ZHENGFANG_HOST + '/CheckCode.aspx'

    @classmethod
    def zhengfang_login(cls):
        # 教务系统登录
        return cls.ZHENGFANG_HOST + '/default2.aspx'

    @classmethod
    def aolan_captcha(cls):
        return cls.AOLAN_HOST + '/VCode.aspx'

    @classmethod
    def aolan_login(cls):
        # 奥兰系统登录
        return cls.AOLAN_HOST + "/LOGIN.ASPX"

    @classmethod
    def lib_login(cls):
        # 图书馆登录
        return cls.LIB_HOST + '/reader/redr_verify.php'

    @classmethod
    def lib_captcha(cls):
        # 图书馆验证码
        return cls.LIB_HOST + '/reader/captcha.php'

    @classmethod
    def card_login(cls):
        # 一卡通登录
        return cls.CARD_HOST + '/Login/LoginBySnoQuery'

    @classmethod
    def card_captcha(cls):
        # 一卡通验证码
        return cls.CARD_HOST + '/Login/GetValidateCode'

    @classmethod
    def card_info(cls):
        # 一卡通基础信息
        return cls.CARD_HOST + '/User/GetCardInfoByAccountNoParm'

    @classmethod
    def card_bill(cls):
        # 一卡通详单
        return cls.CARD_HOST + '/Report/GetMyBill'

    @classmethod
    def card_recharge(cls):
        # 一卡通充值
        return cls.CARD_HOST + '/User/Account_Pay'

    @classmethod
    def card_common(cls):
        # 一卡通Dr.com信息
        return cls.CARD_HOST + '/Tsm/TsmCommon'

    @classmethod
    def card_net_pay(cls):
        # 一卡通网费充值
        return cls.CARD_HOST + '/Tsm/Net_Pay'

    @classmethod
    def card_elec_pay(cls):
        return cls.CARD_HOST + '/Tsm/Elec_Pay'
