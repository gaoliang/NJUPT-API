# encoding: utf-8
import re

from bs4 import BeautifulSoup

from njupt.decorators.zhengfang_logined import zhengfang_logined
from njupt.models.base import Model
from njupt.urls import URL
from njupt.utils import ZhengfangCaptcha

week_re = re.compile(r'第(\d+)-(\d+)周')
courser_indexs_re = re.compile(r'第(\d+(?:,\d+)*)节')
chinese_rome = {
    '一': 1,
    '二': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7
}


class Zhengfang(Model):
    def __init__(self, account=None, password=None):
        super(Zhengfang, self).__init__()
        if account and password:
            self.account = account
            self.login(account, password)

    @zhengfang_logined
    def get_grade(self):
        """
        获取等级考试成绩信息
        :return: list
                [
                    {'date': '20151219',  # 考试日期
                     'name': '全国大学英语四级考试',  # 考试名称
                     'number': '320082152113313',  # 准考证号
                     'score': '547',  # 成绩
                     'semester': '1',  # 学期
                     'year': '2015-2016'  # 学年
                     },
                ]
        """
        soup = self._url2soup(method='get', url=URL.zhengfang_grade(self.account))
        results = []
        for tr in soup.select("#DataGrid1 > tr")[1:]:
            names = ['year', 'semester', 'name', 'number', 'date', 'score']
            result = {}
            for name, td in zip(names, tr.select('td')[:6]):
                result[name] = td.text
            results.append(result)
        return results

    @zhengfang_logined
    def get_schedule(self, week, year=None, semester=None):
        """
        获取指定学期指定周的课表（不传入年份和学期则默认当前学期）
        :param year: 学年 格式为 "2017-2018"
        :param semester: 学期 数字1或2
        :param week: 周次 数字 1-20
        :return: 二维列表schedule，schedule[i][j]代表周i第j节课的课程。 为了方便，i或j为零0的单元均不使用。
                列表的元素为None，代表没有课程，或描述课程信息的dict，dict例如
                {
                    'classroom': '教4－202', 
                    'name': '技术经济学', 
                    'teacher': '储成祥'
                }
        """
        schedule = [[None for col in range(13)] for row in range(8)]
        if year and semester:
            pass
        else:
            r = self.get(url=URL.zhengfang_class_schedule(self.account))
            soup = BeautifulSoup(r.text.replace('<br>', '\n'), 'lxml')
            trs = soup.select("#Table1 > tr")
            for index, tr in enumerate(trs):
                tds = tr.select('td')
                for td in tds:
                    if len(td.text) > 4:  # 筛选出包含课程信息的单元格
                        for courser in td.text.split('\n\n'):
                            info = courser.split()
                            start_week, end_week = map(int, week_re.search(info[1]).groups())
                            courser_indexs = map(int, courser_indexs_re.search(info[1]).groups()[0].split(','))
                            is_odd_week_only = "单周" in info[1]
                            is_even_week_only = "双周" in info[1]
                            week_day = chinese_rome[info[1][1]]
                            courser = {
                                'name': info[0],
                                'teacher': info[2],
                                'classroom': info[3],
                            }
                            if start_week <= week <= end_week:
                                if (week % 2 == 0 and is_odd_week_only) or (week % 2 == 1 and is_even_week_only):
                                    pass
                                else:
                                    for courser_index in courser_indexs:
                                        schedule[week_day][courser_index] = courser
        return schedule

    @zhengfang_logined
    def get_score(self):
        """
        获取课程成绩和绩点等信息
        :return: dict 
                {'gpa': 4.99,  # GPA
                    'coursers': [{
                        'year': '2015-2016',  # 修读学年
                        'semester': '1',  # 修读学期
                        'code': '00wk00003',  # 课程编号
                        'name': '从"愚昧"到"科学"-科学技术简史',  # 课程中文名
                        'attribute': '任选',  # 课程性质
                        'belong': '全校任选课',  # 课程归属
                        'credit': '2.0',  # 学分
                        'point': '',  # 绩点
                        'score': '81',  # 成绩
                        'minorMark': '0',  # 重修标记
                        'make_up_score': '',  # 补考成绩
                        'retake_score': '',  # 重修成绩
                        'college': '网络课程',  # 开课学院
                        'note': '',  # 备注
                        'retake_mark': '0', # 重修标记
                        'english_name': ''  # 课程英文名
                        }, 
                    ]
                }
        """
        viewstate = self._get_viewstate(url=URL.zhengfang_score(self.account))
        data = {
            'ddlXN': '',
            'ddlXQ': '',
            '__VIEWSTATE': viewstate,
            'Button2': '%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
        }
        soup = self._url2soup(method='post', url=URL.zhengfang_score(self.account), data=data)
        result = {'gpa': float(soup.select_one('#pjxfjd > b').text[7:])}
        cols = ['year', 'semester', 'code', 'name', 'attribute', 'belong', 'credit', 'point', 'score', 'minor_mark',
                'make_up_score', 'retake_score', 'college', 'note', 'retake_mark', 'english_name']
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
        :return: {'code': 1, "msg": "登录失败"} 或 {'code': 0, 'msg': '登录成功'}
        """
        captcha_code = ZhengfangCaptcha(self._url2image(URL.zhengfang_captcha())).crack()
        data = {
            "__VIEWSTATE": self._get_viewstate(URL.zhengfang_login()),
            'txtUserName': account,
            'TextBox2': password,
            'RadioButtonList1': "%D1%A7%C9%FA",
            "txtSecretCode": captcha_code,
            "Button1": "",
            "hidPdrs": "",
            "hidsc": ""
        }
        result = self._login_execute(url=URL.zhengfang_login(), data=data)
        if result['code'] == 2:
            # 如果验证码错误，尝试递归重复登录
            return self.login(account, password)
        result['success'] = not result['code']
        if result['success']:
            self.verify = True
        return result

    def _login_execute(self, url=None, data=None):
        r = self.post(url=url, data=data)
        if r.ok:
            if "请到信息维护中完善个人联系方式" in r.text:
                self.account = data['txtUserName']
                # self.cookies.save(ignore_discard=True)  # 保存登录信息cookies
                self.verify = True  # 登陆成功, 修改状态  (后期还可能继续修改)
                # self.cookies.load(filename=settings.COOKIES_FILE, ignore_discard=True)
                return {'code': 0, 'msg': '登录成功'}
            elif "密码错误！！" in r.text:
                return {'code': 1, 'msg': '密码错误！！'}
            elif "验证码不正确！！" in r.text:
                return {'code': 2, 'msg': '验证码不正确！！！'}
            else:
                return {'code': 3, 'msg': '未知错误'}
        else:
            return {'code': 1, "msg": "登录失败"}


if __name__ == "__main__":
    pass
