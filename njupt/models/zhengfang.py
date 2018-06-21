# encoding: utf-8
import re
from datetime import datetime

from bs4 import BeautifulSoup

from njupt.decorators.zhengfang_logined import zhengfang_logined
from njupt.exceptions import AuthenticationException, TemporaryBannedException
from njupt.models.base import Model
from njupt.urls import URL
from njupt.utils import ZhengfangCaptcha, table_to_list, table_to_dict

week_re = re.compile(r'第(\d+)-(\d+)周')
courser_index_re = re.compile(r'第(\d+(?:,\d+)*)节')
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
    def list_exam_grades(self):
        """ 获取等级考试成绩信息
        :rtype list[dict]
        :return 返回元素为等级考试信息字典的列表
        """
        soup = self.get_soup(method='get', url=URL.zhengfang_grade(self.account))
        table = soup.select_one('#DataGrid1')
        result = table_to_list(table, index_cast_dict={
            1: int,
            4: lambda x: datetime.strptime(x, '%Y%m%d')
        })
        return result

    @zhengfang_logined
    def get_gpa(self):
        """
        获取GPA
        :rtype int
        """
        view_state = self._get_viewstate(url=URL.zhengfang_score(self.account))
        data = {
            'ddlXN': '',
            'ddlXQ': '',
            '__VIEWSTATE': view_state,
            'Button2': '%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
        }
        soup = self.get_soup(method='post', url=URL.zhengfang_score(self.account), data=data)
        return float(soup.select_one('#pjxfjd').text[7:])

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
                            courser_index = map(int, courser_index_re.search(info[1]).groups()[0].split(','))
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
                                    for courser_index in courser_index:
                                        schedule[week_day][courser_index] = courser
        return schedule

    @zhengfang_logined
    def get_courses(self):
        """
        获取这学期的选课情况
        :rtype list[dict]
        """
        soup = self.get_soup(method='get', url=URL.zhengfang_courses(self.account))
        trs = soup.select('#DBGrid > tr')[1:]
        courses = []
        for tr in trs:
            tds = [node.text.strip() for node in tr.select('td')]
            name = tds[2]
            teacher = tds[5]
            all_time = tds[8].split(';')
            all_room = tds[9].split(';')
            for time, room in zip(all_time, all_room):
                if time and room:
                    week_start, week_end = map(int, week_re.search(time).groups())
                    courser_index = list(map(int, courser_index_re.search(time).groups()[0].split(',')))
                    week = re.search('{(.*)}', time).groups()[0]
                    if '双周' in week and week_start % 2 == 1:
                        week_start += 1
                    if '单周' in week and week_start % 2 == 0:
                        week_start += 1
                    courses.append(
                        {
                            'day': chinese_rome[time[1]],
                            'name': name,
                            'week': week,
                            'week_start': week_start,
                            'week_end': week_end,
                            'class_start': courser_index[0],
                            'class_end': courser_index[-1],
                            'teacher': teacher,
                            'room': room,
                            'interval': 2 if '单周' in week or '双周' in week else 1,
                        }
                    )
        return courses

    @zhengfang_logined
    def list_exam_scores(self):
        """
        获取参加过的考试的成绩列表
        :rtype list[dict]
        :return 返回一个包含考试成绩信息字典的列表, 注意是所有参加过的考试
        """
        viewstate = self._get_viewstate(url=URL.zhengfang_score(self.account))
        data = {
            'ddlXN': '',
            'ddlXQ': '',
            '__VIEWSTATE': viewstate,
            'Button2': '%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
        }
        soup = self.get_soup(method='post', url=URL.zhengfang_score(self.account), data=data)
        table = soup.select_one('#Datagrid1')
        return table_to_list(table, index_cast_dict={
            1: int,
            6: float,
            7: lambda x: float(x) if x else None,
            8: lambda x: float(x) if x.isdigit() else x
        })

    @zhengfang_logined
    def list_optional_courses(self):
        """获取可选课程列表，对应于教务系统 -> 网上选课 -> 学生选课
        :rtype list[dict]
        :return 可选课程信息列表
        """
        soup = self.get_soup(URL.zhengfang_list_optional_courses(self.account))
        if len(str(soup)) < 100:
            raise TemporaryBannedException('选课三秒防刷')
        table = soup.select_one('#kcmcgrid')
        result = table_to_list(table, remove_index_list=[8], index_cast_dict={
            4: int,
            9: int
        })
        return result[:-1]  # 最后多了一个空行

    @zhengfang_logined
    def get_course_info(self, courser_code):
        """
        获取课程的简介信息
        :param courser_code: 课程代码
        :rtype: dict
        """
        soup = self.get_soup(URL.zhengfang_get_course_info(account=self.account, course_code=courser_code))
        table = soup.select_one('#Table1')
        return table_to_dict(table)

    def login(self, account, password):
        """登录教务系统 jwxt.njupt.edu.cn
        :param account: 南邮学号
        :param password: 密码
        :return: {'code': 1, "msg": "登录失败"} 或 {'code': 0, 'msg': '登录成功'}
        """
        captcha_code = ZhengfangCaptcha(self.get_image(URL.zhengfang_captcha())).crack()
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
        else:
            raise AuthenticationException(result['msg'])
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
