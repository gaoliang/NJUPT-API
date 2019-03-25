import re
from datetime import datetime

from bs4 import BeautifulSoup

from njupt.base import API
from njupt.exceptions import NjuptException, AuthenticationException


class RunningMan(API):
    """ 体育部早操查询接口

    :param str student_id: 学号
    :param str name: 姓名

    :raise: :class:`njupt.exceptions.AuthenticationException`

    >>> rm = RunningMan(student_id='B18888888', name='杨震')
    """

    def __init__(self, student_id, name):
        super().__init__()
        self.student_id = student_id
        self.name = name
        self.digit_pattern = re.compile(r'\d+')
        self.space_pattern = re.compile(r'\s+')

    def check(self):
        """
        查询跑操次数

        :rtype: dict

        >>> rm.check()
        {'origin_number': 10, 'extra_number': 1, 'date_list': []}

        """
        url = 'http://zccx.tyb.njupt.edu.cn/student'
        data = {
            'number': self.student_id,
            'name': self.name
        }
        response = self.post(url=url, data=data, allow_redirects=False)
        status = response.status_code
        if status == 302:
            raise AuthenticationException("学号、姓名不对应")

        soup = BeautifulSoup(response.content, 'lxml')

        number_text = soup.select('.list-group')[0].get_text()

        origin_number = self.digit_pattern.findall(number_text)[0]
        try:
            extra_number = self.digit_pattern.findall(number_text)[1]
        except IndexError:
            extra_number = 0

        try:
            raw_data_list = soup.find('tbody').find_all('tr')
            date_list = []
            for item in raw_data_list:
                date_str = re.sub(self.space_pattern, '', item.get_text())
                date = datetime.strptime(date_str, '%Y年%m月%d日%H时%M分')
                date_list.append(date)

        except AttributeError:
            date_list = []

        return {
            'origin_number': origin_number,
            'extra_number': extra_number,
            'date_list': date_list
        }
