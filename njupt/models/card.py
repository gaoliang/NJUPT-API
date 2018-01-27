# encoding: utf-8
import base64
import datetime
import json

from njupt.models.base import Model
from njupt.urls import URL
from njupt.utils import CardCaptcha


class Card(Model):
    def __init__(self, account=None, password=None):
        super(Card, self).__init__()
        self.aid = None
        self.inner_account = None
        if account and password:
            self.account = account
            self.login(account, password)

    def login(self, account, password):
        """
        登录校园卡网站
        :param account: 校园卡卡号
        :param password: 校园卡查询密码
        :return: {'code': 1, "msg": "登录失败，请重试"} 或 {'code': 0, 'msg': '登录成功'}
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
        if result['code'] == 2:
            # 如果验证码错误，尝试递归重复登录
            return self.login(account, password)
        result['success'] = not result['code']
        return result

    def _login_execute(self, url=None, data=None):
        result = self._url2json(url=url, data=data, method="post")
        if result['IsSucceed']:
            return {'code': 0, 'msg': '登录成功'}
        else:
            if result['Msg'] == "验证码错误":
                return {'code': 2, 'msg': '验证码错误'}
            else:
                return {'code': 1, 'msg': result['Msg']}

    def _get_inner_account(self):
        """
        获取对应的内部账号，部分接口参数需要
        :return: 校园卡号对应的系统内部账号 
        """
        if not self.inner_account:
            info = self._url2json(URL.card_info(), method='post', data={'json': True})
            result = json.loads(info['Msg'])
            self.inner_account = result['query_card']['card'][0]['account']
        return self.inner_account

    def _get_aid(self):
        """获取内部的aid"""
        if not self.aid:
            data = {
                'jsondata': '{"query_applist": {"apptype": "net"}}',
                'funname': 'synjones.onecard.query.applist',
                'json': True
            }
            result = self._url2json(url=URL.card_net(), data=data, method='post')
            result = json.loads(result['Msg'])
            self.aid = result['query_applist']['applist'][0]['aid']
        return self.aid

    def get_balance(self):
        """
        查询余额
        :return: dict
                {
                    'balance': 10.01,  # 到账余额
                    'unsettle_balance': 0.01  # 过渡余额
                    'total': 10.02  # 总余额
                }
        """
        info = self._url2json(URL.card_info(), method='post', data={'json': True})
        result = json.loads(info['Msg'])
        balance = int(result['query_card']['card'][0]['db_balance']) / 100  # 到账余额
        unsettle_balance = int(result['query_card']['card'][0]['unsettle_amount']) / 100  # 过渡余额
        return {
            'balance': balance,  # 到账余额
            'unsettle_balance': unsettle_balance,  # 过渡余额
            'total': balance + unsettle_balance,  # 总余额
        }

    def get_net_balance(self):
        """
        获取Dr.com的上网费用余额
        :return: float  2.33
        """
        data = {
            'jsondata': '{"query_net_info": {"aid": "%s", "account": "%s", "payacc": ""}}'  # 无法使用format格式化
                        % (self._get_aid(), self._get_inner_account()),
            'funname': 'synjones.onecard.query.net.info',
            'json': True,
        }
        result = self._url2json(url=URL.card_net(), data=data, method='post')
        result = json.loads(result['Msg'])
        return float(result['query_net_info']['errmsg'][12:][:-1])

    def recharge(self, amount=0.01):
        """
        从绑定的银行卡中扣款充值余额
        :param amount: 充值金额，默认为0.01元
        :return: dict
            {   
                'success':True  # 转账是否成功
                'code': 0,  # 状态码
                'msg': '转账成功'  # 附加信息
            }
        """
        data = {
            'account': self._get_inner_account(),
            'acctype': '###',
            'tranamt': int(100 * amount),
            'qpwd': '',
            'paymethod': '2',
            'paytype': '使用绑定的默认账号',
            'client_type': 'web',
            'json': True,
        }
        info = self._url2json(URL.card_recharge(), 'post', data)
        info = json.loads(info['Msg'])['transfer']
        result = {
            'code': int(info['retcode']),
            'msg': info['errmsg'],
            'success': not bool(int(info['retcode']))
        }
        return result

    def recharge_net(self, amount=0.01):
        """
        充值网费（从校园卡余额中）
        :param amount: 金额 如 2.33
        :return: dict
            {
                'success':True, 
                'code' : 0,
                'Msg' : '充值成功'
            }
        """
        data = {
            'paytype': 1,
            'aid': self._get_aid(),
            'account': self._get_inner_account(),
            'tran': int(amount * 100),
            'netacc': '{"netacc": "", "bal": null, "pkgid": null, "lostflag": null, "freezeflag": null, '
                      '"expflag": null,"statustime": null, "duration": null, "starttime": null, "pkgtab": []}',
            'pkgflag': 'none',
            'pkg': '{}',
            'acctype': '###',
            'qpwd': '',
            'json': True
        }
        result = self._url2json(url=URL.card_net_pay(), method='post', data=data)
        result = json.loads(result['Msg'])
        return {
            'success': not int(result['pay_net_gdc']['retcode']),
            'code': int(result['pay_net_gdc']['retcode']),
            'msg': result['pay_net_gdc']['errmsg']
        }

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
                [{'balance': 39.71,  # 余额
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
                    'balance': row['CARDBAL'],
                    'department': row['MERCNAME'].strip(),
                    'comment': row['JDESC'].strip(),
                    'change': row['TRANAMT'],
                    'week': row['XQ'],
                    'time': row['OCCTIME'],
                    'type': row['TRANNAME'].strip(),
                })
        return result


if __name__ == "__main__":
    card = Card()
