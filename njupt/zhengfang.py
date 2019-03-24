# encoding: utf-8
import re
from datetime import datetime

from bs4 import BeautifulSoup

from njupt.base import API
from njupt.exceptions import AuthenticationException, TemporaryBannedException
from njupt.utils import ZhengfangCaptcha, table_to_list, table_to_dict, login_required

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


class Zhengfang(API):
    """南邮正方教务

    :param str account: 南邮学号
    :param str password: 密码
    :raise: :class:`njupt.exceptions.AuthenticationException`

    >>> zf = Zhengfang(account='B11111111', password='xxx')
    """

    class URLs:
        HOST = "http://jwxt.njupt.edu.cn"

        SCORE = HOST + '/xscj_gc.aspx?xh={account}&xm=%B8%DF%C1%C1&gnmkdm=N121605'
        SCHEDULE = HOST + '/xskbcx.aspx?xh={account}&xm=%B8%DF%C1%C1&gnmkdm=N121603'
        GRADE = HOST + '/xsdjkscx.aspx?xh={account}&xm=%B8%DF%C1%C1&gnmkdm=N121606'
        SELECTED_COURSES = HOST + '/xsxkqk.aspx?xh={account}&xm=%B8%DF%C1%C1&gnmkdm=N121615'
        OPTIONAL_COURSES = HOST + '/xsxk.aspx?xh={account}&xm=%B8%DF%C1%C1&gnmkdm=N121101'
        COURSE_INFO = HOST + '/kcxx.aspx?xh={account}&kcdm={course_code}&xkkh=%26nbsp%3bk'
        # 教务系统验证码
        CAPTCHA = HOST + '/CheckCode.aspx'
        # 教务系统登录
        LOGIN = HOST + '/default2.aspx'

    def __init__(self, account=None, password=None):
        super(Zhengfang, self).__init__()
        if account and password:
            self.account = account
            self.login(account, password)

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
        soup = self.get_soup(method='get', url=self.URLs.GRADE.format(account=self.account))
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
        view_state = self._get_viewstate(url=self.URLs.SCORE.format(account=self.account))
        data = {
            'ddlXN': '',
            'ddlXQ': '',
            '__VIEWSTATE': view_state,
            'Button2': '%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
        }
        soup = self.get_soup(method='post', url=self.URLs.SCORE.format(account=self.account), data=data)
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
            r = self.get(url=self.URLs.SCHEDULE.format(account=self.account))
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
        r = self.get(url=self.URLs.SELECTED_COURSES.format(account=self.account))
        # soup = self.get_soup(method='get', url=self.URLs.SELECTED_COURSES.format(account=self.account))
        # 编码参考：
        # http://bbs.chinaunix.net/thread-3610023-1-1.html
        soup = BeautifulSoup(r.content, fromEncoding="gb18030")
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
        viewstate = self._get_viewstate(url=self.URLs.SCORE.format(account=self.account))
        data = {
            'ddlXN': '',
            'ddlXQ': '',
            '__VIEWSTATE': viewstate,
            'Button2': '%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
        }
        soup = self.get_soup(method='post', url=self.URLs.SCORE.format(account=self.account), data=data)
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
        soup = self.get_soup(self.URLs.OPTIONAL_COURSES.format(account=self.account))
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
        soup = self.get_soup(self.URLs.COURSE_INFO.format(account=self.account, course_code=courser_code))
        table = soup.select_one('#Table1')
        return table_to_dict(table)

    def login(self, account, password):
        # FIXME: 登录不可靠
        captcha_code = ZhengfangCaptcha(self.get_image(self.URLs.CAPTCHA)).crack()
        data = {
            "__VIEWSTATE": self._get_viewstate(self.URLs.LOGIN),
            'txtUserName': account,
            'TextBox2': password,
            'RadioButtonList1': "%D1%A7%C9%FA",
            "txtSecretCode": captcha_code,
            "Button1": "",
            "hidPdrs": "",
            "hidsc": ""
        }
        result = self._login_execute(url=self.URLs.LOGIN, data=data)
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
