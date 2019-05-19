# encoding: utf-8
import re
from datetime import datetime

from bs4 import BeautifulSoup

from njupt.base import APIWrapper
from njupt.exceptions import TemporaryBannedException, AuthenticationException
from njupt.utils import table_to_list, table_to_dict, login_required, ZhengfangCaptcha

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


class Zhengfang:
    """南邮正方教务, sso登录方式参见 :class:`njupt.SSO` 单点登录

    >>> # 👍 推荐使用sso登录来获取正方实例，速度更快
    >>> from njupt import SSO
    >>> sso = SSO(username='B12345678', password='abcdefgh') # 账号密码为my.njupt.edu.cn账号密码
    >>> zf = sso.zhengfang()

    >>> # 😐 传统的正方账号密码方式, 速度慢
    >>> from njupt import Zhengfang
    >>> zf = Zhengfang(username='B12345678', password='abcdefgh')
    """

    class URLs:
        HOST = "http://jwxt.njupt.edu.cn"

        SCORE = HOST + '/xscj_gc.aspx?xh={username}&gnmkdm=N121605'
        SCHEDULE = HOST + '/xskbcx.aspx?xh={username}&gnmkdm=N121603'
        GRADE = HOST + '/xsdjkscx.aspx?xh={username}&gnmkdm=N121606'
        SELECTED_COURSES = HOST + '/xsxkqk.aspx?xh={username}&gnmkdm=N121615'
        OPTIONAL_COURSES = HOST + '/xsxk.aspx?xh={username}&gnmkdm=N121101'
        COURSE_INFO = HOST + '/kcxx.aspx?xh={username}&kcdm={course_code}&xkkh=%26nbsp%3bk'
        # 教务系统登录
        USERNAME_LOGIN = HOST + '/default2.aspx'
        # 教务系统验证码
        CAPTCHA = HOST + '/CheckCode.aspx'
        # SSO 跳转
        SSO_LOGIN = 'http://202.119.226.235:8017/im/application/sso.zf?login=7CF3D066D16B5374E053D8E277CAC84D'

    def __init__(self, username=None, password=None, sso_session=None):
        super().__init__()
        if sso_session:
            self.s = sso_session
            self.username = sso_session.username
            self.login_by_sso()
            self.verified = True
        else:
            self.s = APIWrapper()
            self.username = username
            self.password = password
            self.login_by_username()
            self.verified = True

    def login_by_sso(self):
        self.s.get(self.URLs.SSO_LOGIN)
        self.verified = True

    def login_by_username(self):
        captcha_code = ZhengfangCaptcha(self.s.get_image(self.URLs.CAPTCHA)).crack()
        data = {
            "__VIEWSTATE": self.s._get_viewstate(self.URLs.USERNAME_LOGIN),
            'txtUserName': self.username,
            'TextBox2': self.password,
            'RadioButtonList1': "%D1%A7%C9%FA",
            "txtSecretCode": captcha_code,
            "Button1": "",
            "hidPdrs": "",
            "hidsc": ""
        }
        r = self.s.post(url=self.URLs.USERNAME_LOGIN, data=data)
        if r.ok:
            if "请到信息维护中完善个人联系方式" in r.text:
                self.verified = True
                return {'success': True, 'msg': '登录成功'}
            elif "密码错误" in r.text:
                raise AuthenticationException('密码错误')
            elif "验证码不正确" in r.text:
                return self.login_by_username()
            else:
                raise AuthenticationException('未知错误')

    @login_required
    def list_exam_grades(self):
        """ 获取等级考试成绩信息

        :rtype: list of dict
        :return: 列表，内容为每次等级考试的信息

        >>> zf.list_exam_grades()
        [
            {
                '学年': '2015-2016',
                '学期': 1,
                '等级考试名称': '全国大学英语四级考试',
                '准考证号': '320082152113313',
                '考试日期': datetime.datetime(2015, 12, 19, 0, 0),
                '成绩': '710'
                '写作成绩': '',
                '综合成绩': ''
            },
            ...
        ]
        """
        soup = self.s.get_soup(method='get', url=self.URLs.GRADE.format(username=self.username))
        table = soup.select_one('#DataGrid1')
        result = table_to_list(table, index_cast_dict={
            1: int,
            4: lambda x: datetime.strptime(x, '%Y%m%d')
        })
        return result

    @login_required
    def get_gpa(self):
        """获取GPA

        :rtype: int

        >>> zf.get_gpa()
        5.0
        """
        view_state = self.s._get_viewstate(url=self.URLs.SCORE.format(username=self.username))
        data = {
            'ddlXN': '',
            'ddlXQ': '',
            '__VIEWSTATE': view_state,
            'Button2': '%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
        }
        soup = self.s.get_soup(method='post', url=self.URLs.SCORE.format(username=self.username), data=data)
        return float(soup.select_one('#pjxfjd').text[7:])

    @login_required
    def get_schedule(self, week, year=None, semester=None):
        """
        获取指定学期指定周的课表（不传入年份和学期则默认当前学期), 不推荐使用

        :param year: 学年 格式为 "2017-2018"
        :param semester: 学期 数字1或2
        :param week: 周次 数字 1-20
        :return: 二维列表schedule，schedule[i][j]代表周i第j节课的课程。 为了方便，i或j为零0的单元均不使用。
                列表的元素为None，代表没有课程，或描述课程信息的dict

        >>> zf.get_schedule(week=1, year='2017-2018', semester=1)
        [
            {
                'classroom': '教4－202',
                'name': '技术经济学',
                'teacher': '储成祥'
            }
        ]
        """
        schedule = [[None for col in range(13)] for row in range(8)]
        if year and semester:
            pass
        else:
            r = self.s.get(url=self.URLs.SCHEDULE.format(username=self.username))
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

    @login_required
    def get_courses(self):
        """获取这学期的选课情况

        :return:  格式参看例子，期中interval为1则为单周，2则为双周。 这些信息足够生成课表了
        :rtype: list of dict

        >>> zf.get_courses()
        [
            {
                'class_start': 8,
                'class_end': 9,
                'day': 1,
                'name': '市场营销',
                'room': '教4－101',
                'teacher': '王波(男)',
                'week': '第1-15周|单周',
                'interval': 2,
                'week_end': 15,
                'week_start': 1
            },
            ...
        ]
        """
        r = self.s.get(url=self.URLs.SELECTED_COURSES.format(username=self.username))
        # soup = self.get_soup(method='get', url=self.URLs.SELECTED_COURSES.format(username=self.username))
        # 编码参考：
        # http://bbs.chinaunix.net/thread-3610023-1-1.html
        soup = BeautifulSoup(r.content, from_encoding="gb18030", features='lxml')
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

    @login_required
    def list_exam_scores(self):
        """获取参加过的考试的成绩列表

        :rtype: list[dict]
        :return: 返回一个包含考试成绩信息字典的列表, 注意是所有参加过的考试

        >>> zf.list_exam_scores()
        [
            {
                '备注': '',
                '学分': 3.0,
                '学年': '2016-2017',
                '学期': 1,
                '学院名称': '电子科学与工程学院',
                '成绩': 90.0,
                '绩点': 4.0,
                '补考成绩': '',
                '课程代码': 'B0400111S',
                '课程名称': '模拟电子线路C',
                '课程归属': '',
                '课程性质': '必修',
                '课程英文名称': '',
                '辅修标记': '0',
                '重修成绩': '',
                '重修标记': '0'
            },
            ...
        ]

        """
        viewstate = self.s._get_viewstate(url=self.URLs.SCORE.format(username=self.username))
        data = {
            'ddlXN': '',
            'ddlXQ': '',
            '__VIEWSTATE': viewstate,
            'Button2': '%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
        }
        soup = self.s.get_soup(method='post', url=self.URLs.SCORE.format(username=self.username), data=data)
        table = soup.select_one('#Datagrid1')
        return table_to_list(table, index_cast_dict={
            1: int,
            6: float,
            7: lambda x: float(x) if x else None,
            8: lambda x: float(x) if x.isdigit() else x
        })

    @login_required
    def get_gpa_under_pku(self):
        """获取按照北大GPA算法计算的绩点

        :return: 北大算法绩点，注意是计算了任选课和重修课的成绩

        >>>zf.get_gpa_under_pku()
        """
        scores = self.list_exam_scores()
        effective_courses = [score for score in scores]
        total_credits = 0
        academic_credits = 0
        for score in effective_courses:
            if score['成绩'] == '优秀':
                score['成绩'] = 90
            elif score['成绩'] == '良好':
                score['成绩'] = 80
            elif score['成绩'] == '中等':
                score['成绩'] = 70
            elif score['成绩'] == '合格':
                score['成绩'] = 60
            elif score['成绩'] == '不合格':
                score['成绩'] = 59
            if score['重修成绩'] != '':
                rehearsal_course = score
                rehearsal_course['成绩'] = float(rehearsal_course['重修成绩'])
                rehearsal_course['重修成绩'] = ''
                effective_courses.append(rehearsal_course)

        for score in effective_courses:
            if score['成绩'] > 60:
                score['绩点'] = float('%.2f' % (4 - 3 * (100 - score['成绩']) ** 2 / 1600))
            else:
                if score['补考成绩'] == '及格':
                    score['绩点'] = 1.0
                else:
                    score['绩点'] = 0.0
            academic_credits += score['学分'] * score['绩点']
            total_credits += score['学分']
        return float('%.2f' % (academic_credits / total_credits))

    @login_required
    def get_gpa_under_zju(self):
        """获取按照浙大GPA算法计算的绩点

        :return: 浙大算法绩点，注意是计算了任选课和重修课的成绩

        >>> zf.get_gpa_under_zju()

        """
        scores = self.list_exam_scores()
        effective_courses = [score for score in scores]
        total_credits = 0
        academic_credits = 0
        for score in effective_courses:
            if score['成绩'] == '优秀':
                score['成绩'] = 90
            elif score['成绩'] == '良好':
                score['成绩'] = 80
            elif score['成绩'] == '中等':
                score['成绩'] = 70
            elif score['成绩'] == '合格':
                score['成绩'] = 60
            elif score['成绩'] == '不合格':
                score['成绩'] = 59
            if score['重修成绩'] != '':
                rehearsal_course = score
                rehearsal_course['成绩'] = float(rehearsal_course['重修成绩'])
                rehearsal_course['重修成绩'] = ''
                effective_courses.append(rehearsal_course)

        for score in effective_courses:
            if score['成绩'] >= 85:
                score['绩点'] = 4.0
            elif 60 <= score['成绩'] <= 84:
                score['绩点'] = (score['成绩'] - 60) * 0.1 + 1.5
            else:
                if score['补考成绩'] == '及格':
                    score['绩点'] = 1.5
                else:
                    score['绩点'] = 0.0
            academic_credits += score['学分'] * score['绩点']
            total_credits += score['学分']
        return float('%.2f' % (academic_credits / total_credits))

    @login_required
    def list_optional_courses(self):
        """获取可选课程列表，对应于教务系统 -> 网上选课 -> 学生选课

        :rtype: list of dict
        :return: 可选课程信息列表
        :raise: :class:`njupt.exceptions.TemporaryBannedException`
        """
        soup = self.s.get_soup(self.URLs.OPTIONAL_COURSES.format(username=self.username))
        if len(str(soup)) < 100:
            raise TemporaryBannedException('选课三秒防刷')
        table = soup.select_one('#kcmcgrid')
        result = table_to_list(table, remove_index_list=[8], index_cast_dict={
            4: int,
            9: int
        })
        return result[:-1]  # 最后多了一个空行

    @login_required
    def get_course_info(self, courser_code):
        """
        获取课程的简介信息

        :param courser_code: 课程代码
        :rtype: dict

        """
        soup = self.s.get_soup(self.URLs.COURSE_INFO.format(username=self.username, course_code=courser_code))
        table = soup.select_one('#Table1')
        return table_to_dict(table)
