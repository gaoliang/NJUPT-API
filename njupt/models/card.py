# encoding: utf-8
import base64
import datetime
import json
from pprint import pprint

from njupt.models.base import Model
from njupt.urls import URL
from njupt.utils import CardCaptcha


class Card(Model):
    def __init__(self, account=None, password=None):
        super(Card, self).__init__()
        if account and password:
            self.account = account
            self.login(account, password)

    def login(self, account, password):
        """
        登录校园卡网站
        :param account: 校园卡卡号
        :param password: 校园卡查询密码
        :return: {'errorCode': 1, "msg": "登录失败，请重试"} 或 {'errorCode': 0, 'msg': '登录成功'}
        """
        captcha_code = CardCaptcha(self._url2image(URL.card_captcha())).crack()
        data = {
            "sno": account,
            "pwd": base64.b64encode(str(password).encode("utf8")),
            "ValiCode": captcha_code,
            "remember": 1,
            "uclass": 1,
            "zqcode": "",
            "json": True,
        }

        result = self._login_execute(url=URL.card_login(), data=data)
        if result['errorCode'] == 2:
            # 如果验证码错误，尝试递归重复登录
            return self.login(account, password)
        return result

    def _login_execute(self, url=None, data=None):
        result = self._url2json(url=url, data=data, method="post")
        if result['IsSucceed']:
            return {'errorCode': 0, 'msg': '登录成功'}
        else:
            if result['Msg'] == "验证码错误":
                return {'errorCode': 2, 'msg': '验证码错误'}
            else:
                return {'errorCode': 1, 'msg': result['Msg']}

    def _get_inner_account(self):
        """
        获取对应的内部账号，部分接口参数需要
        :return: 校园卡号对应的系统内部账号 
        """
        info = self._url2json(URL.card_info(), method='post', data={'json': True})
        result = json.loads(info['Msg'])
        return result['query_card']['card'][0]['account']

    def get_balance(self):
        """
        查询余额
        :return: int 余额
        """
        info = self._url2json(URL.card_info(), method='post', data={'json': True})
        result = json.loads(info['Msg'])
        return int(result['query_card']['card'][0]['db_balance']) / 100

    def get_bill(self, start_date=(datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                 end_date=datetime.datetime.now().strftime("%Y-%m-%d"), rows=100, page=1):
        """
        查询校园卡消费记录，默认为最近一个月的消费记录
        :param start_date: 查询区间的开始时间 "2017-12-27"
        :param end_date:  查询区间的结束时间 "2018-01-26"
        :param rows: 一次查询返回的最大记录数量,默认为100条记录
        :param page: 如果结果数量有多页，决定返回第几页。
        :return: list 
            {'recodes': 
                [{'balances': 39.71,  # 余额
                  'change': -5, # 变动
                  'comment': '未知系统,交电费', # 注释
                  'department': '仙林售电处', # 操作部门
                  'time': '2018-01-26 20:55:40', # 时间
                  'type': '代扣代缴', # 类型
                  'week': '星期五'}, # 星期
                 {'balances': 39.71,
                  'change': -7.5,
                  'comment': '',
                  'department': '一餐厅二楼清真食堂',
                  'time': '2018-01-24 17:09:36',
                  'type': '持卡人消费',
                  'week': '星期三'}
                   ... ],
            'total': 52 # 总的记录数
            'total_pages':2 # 总页数
            'page':1  # 当前的页码
            }
        """
        data = {
            "sdate": start_date,
            "edate": end_date,
            "account": self._get_inner_account(),
            "page": page,
            "rows": rows
        }
        temp = self._url2json(url=URL.card_bill(), method="post", data=data)
        result = {'total': temp['total'], 'recodes': [], 'total_pages': temp['total'] // rows + 1, 'page': page}
        if temp['rows']:
            for row in temp['rows']:
                result['recodes'].append({
                    'balances': row['CARDBAL'],
                    'department': row['MERCNAME'].strip(),
                    'comment': row['JDESC'].strip(),
                    'change': row['TRANAMT'],
                    'week': row['XQ'],
                    'time': row['OCCTIME'],
                    'type': row['TRANNAME'].strip(),
                })
        return result


if __name__ == "__main__":
    pass
