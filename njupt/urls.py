# encoding: utf-8
"""
通用ＵＲＬ类,NJUPT各个网站的ＵＲＬ接口地址
"""


class URL(object):
    HOST = "https://www.njupt.edu.cn"
    ZHENGFANG_HOST = "http://jwxt.njupt.edu.cn"
    AOLAN_HOST = "http://stu.njupt.edu.cn"
    LIB_HOST = "http://202.119.228.6:8080"

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
    def zhengfang_list_optional_courses(cls, account):
        return cls.ZHENGFANG_HOST + '/xsxk.aspx?xh={}&xm=%B8%DF%C1%C1&gnmkdm=N121101'.format(account)

    @classmethod
    def zhengfang_get_course_info(cls, account, course_code):
        return cls.ZHENGFANG_HOST + '/kcxx.aspx?xh={}&kcdm={}&xkkh=%26nbsp%3bk'.format(account, course_code)

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
