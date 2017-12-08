# encoding: utf-8
from bs4 import BeautifulSoup

from njupt import settings
from njupt.decorators.zhengfang_logined import zhengfang_logined
from njupt.models.base import Model
from njupt.urls import URL


class Zhengfang(Model):
    def __init__(self, account=None, password=None):
        super(Zhengfang, self).__init__()
        if account and password:
            self.account = account
            self.login(account, password)

    @zhengfang_logined
    def get_class_schedule(self, week, year=None, semester=None):
        """
        获取指定学期指定周的课表（不传入年份和学期则默认当前学期）
        :param year: 学年 格式为 "2017-2018"
        :param semester: 学期 数字1或2
        :param week: 周次 数字 1-20
        :return: 
        """
        if year and semester:
            pass
        else:
            r = self._execute(method='get', url=URL.jwxt_class_schedule(self.account))
            soup = BeautifulSoup(r.text.replace('<br>', '\n'), 'lxml')
            trs = soup.select("#Table1 > tr")
            schedule = {}
            for tr in trs:
                tds = tr.select('td')
                for td in tds:
                    print(td.text.split())

    @zhengfang_logined
    def get_score(self):
        """
        获取课程成绩和绩点等信息
        :return: dict 
                {'gpa': 4.99,
                    'coursers': [{
                        'year': '2015-2016',
                        'semester': '1',
                        'code': '00wk00003',
                        'name': '从"愚昧"到"科学"-科学技术简史',
                        'attribute': '任选',
                        'belong': '全校任选课',
                        'credit': '2.0',
                        'point': '',
                        'score': '81',
                        'minorMark': '0',
                        'makeUpScore': '',
                        'retakeScore': '',
                        'college': '网络课程',
                        'note': '',
                        'retakeMark': '0',
                        'englishName': ''
                        }, 
                        ]
                    }
        """
        viewstate = self._get_viewstate(url=URL.jwxt_grade(self.account))
        data = {
            'ddlXN': '',
            'ddlXQ': '',
            '__VIEWSTATE': viewstate,
            'Button2': '%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
        }
        r = self._execute(method='post', url=URL.jwxt_grade(self.account), data=data)
        soup = BeautifulSoup(r.text, 'lxml')
        result = {'gpa': float(soup.select_one('#pjxfjd > b').text[7:])}
        cols = ['year', 'semester', 'code', 'name', 'attribute', 'belong', 'credit', 'point', 'score', 'minorMark',
                'makeUpScore', 'retakeScore', 'college', 'note', 'retakeMark', 'englishName']
        #  学年 学号 课程代码 课程名称 课程性质 课程归属 学分 绩点 成绩 辅修标记 补考成绩 重修成绩 开课学院 备注 重修标记
        coursers = []
        for tr in soup.select('#Datagrid1  > tr')[1:]:
            courser = {}
            for col, td in zip(cols, tr.select('td')):
                value = td.text.strip()
                courser[col] = value
            coursers.append(courser)
        result['coursers'] = coursers
        return result

    def login(self, account, password):
        """
        登录教务系统 jwxt.njupt.edu.cn
        :param account: 南邮学号
        :param password: 密码
        :return: {'r': 1, "msg": "登录失败"} 或 {'r': 0, 'msg': '登录成功'}
        """
        data = {
            "__VIEWSTATE": self._get_viewstate(URL.jwxt_login()),
            'txtUserName': account,
            'TextBox2': password,
            'RadioButtonList1': "%D1%A7%C9%FA",
            "txtSecretCode": self._get_captcha(URL.jwxt_captcha()),
            "Button1": "",
            "hidPdrs": "",
            "hidsc": ""
        }
        result = self._login_execute(url=URL.jwxt_login(), data=data)
        if result['r'] == 2:
            # 如果验证码错误，尝试递归重复登录
            return self.login(account, password)
        return result

    def _login_execute(self, url=None, data=None):
        r = self._execute(method="post", url=url, data=data)
        if r.ok:
            if "请到信息维护中完善个人联系方式" in r.text:
                self.account = data['txtUserName']
                self.cookies.save(ignore_discard=True)  # 保存登录信息cookies
                self.cookies.load(filename=settings.COOKIES_FILE, ignore_discard=True)
                return {'r': 0, 'msg': '登录成功'}
            elif "密码错误！！" in r.text:
                return {'r': 1, 'msg': '密码错误！！'}
            elif "验证码不正确！！" in r.text:
                return {'r': 2, 'msg': '验证码不正确！！！'}
            else:
                return {'r': 3, 'msg': '未知错误'}
        else:
            return {'r': 1, "msg": "登录失败"}
