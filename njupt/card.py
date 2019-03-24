# encoding: utf-8
import base64
import datetime
import json
import re

from njupt.exceptions import NjuptException, AuthenticationException
from njupt.base import API
from njupt.utils import login_required
from njupt.utils.captchas.card import CardCaptcha

AIDS = {
    'elec_xianlin': '0030000000005101',
    'elec_sanpailou': '0030000000005102',
    'net': '0030000000000301'
}


class Card(API):
    """
    一卡通相关接口

    :param str account: 一卡通卡号
    :param str password: 一卡通查询密码

    :raise: :class:`njupt.exceptions.AuthenticationException`

    >>> card = Card(account='B15080500', password='sssss')
    """

    class URLs:
        HOST = "http://yktapp.njupt.edu.cn:8070"
        # 登录地址
        LOGIN = HOST + '/Login/LoginBySnoQuery'
        # 一卡通验证码
        CAPTCHA = HOST + '/Login/GetValidateCode'
        # 一卡通基础信息
        INFO = HOST + '/User/GetCardInfoByAccountNoParm'
        # 一卡通消费记录
        BILL = HOST + '/Report/GetMyBill'
        # 一卡通充值
        RECHARGE = HOST + '/User/Account_Pay'
        # 一卡通Dr.com信息
        COMMON = HOST + '/Tsm/TsmCommon'
        # 一卡通网费充值
        NET_PAY = HOST + '/Tsm/Net_Pay'
        # 电费充值
        ELEC_PAY = HOST + '/Tsm/Elec_Pay'

    def __init__(self, account=None, password=None):
        super(Card, self).__init__()
        self.aid = None
        # 该系统使用aid区分业务类型
        self.inner_account = None
        if account and password:
            self.account = account
            self._login(account, password)

    def _login(self, account, password):
        captcha_code = CardCaptcha(self.get_image(self.URLs.CAPTCHA)).crack()
        data = {
            "sno": account,
            "pwd": base64.b64encode(str(password).encode("utf8")),
            "ValiCode": captcha_code,
            "remember": 1,
            "uclass": 1,
            "zqcode": "",
            "json": True,
        }

        result = self._login_execute(url=self.URLs.LOGIN, data=data)
        if result['code'] == 2:
            # 如果验证码错误，尝试递归重复登录
            return self._login(account, password)
        result['success'] = not result['code']
        if result['success']:
            self.verify = True
        else:
            raise AuthenticationException(result['msg'])
        return result

    def _login_execute(self, url=None, data=None):
        result = self.get_json(url=url, data=data, method="post")
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

        :return: 一卡通号对应的系统内部账号
        """
        if not self.inner_account:
            info = self.get_json(self.URLs.INFO, method='post', data={'json': True})
            result = json.loads(info['Msg'])
            self.inner_account = result['query_card']['card'][0]['account']
        return self.inner_account

    @login_required
    def get_balance(self):
        """
        查询余额

        :return: 包含 过度余额、到账余额、总余额的dict
        :rtype: dict of (str, float)

        >>> card.get_balance()
        {'balance': 10.01, 'unsettle_balance': 0.01, 'total': 10.02}
        """
        info = self.get_json(self.URLs.INFO, method='post', data={'json': True})
        result = json.loads(info['Msg'])
        balance = int(result['query_card']['card'][0]['db_balance']) / 100  # 到账余额
        unsettle_balance = int(result['query_card']['card'][0]['unsettle_amount']) / 100  # 过渡余额
        return {
            'balance': balance,  # 到账余额
            'unsettle_balance': unsettle_balance,  # 过渡余额
            'total': balance + unsettle_balance,  # 总余额
        }

    @login_required
    def get_net_balance(self):
        """
        获取Dr.com的上网费用余额

        :return: dr.com的余额
        :rtype: float

        >>> card.get_net_balance()
        2.33
        """
        data = {
            'jsondata': '{"query_net_info": {"aid": "%s", "account": "%s", "payacc": ""}}'  # 无法使用format格式化
                        % (AIDS['net'], self._get_inner_account()),
            'funname': 'synjones.onecard.query.net.info',
            'json': True,
        }
        result = self.get_json(url=self.URLs.COMMON, data=data, method='post')
        result = json.loads(result['Msg'])
        return float(re.search(r'余额(\d*\.\d*)元', result['query_net_info']['errmsg']).groups()[0])

    @login_required
    def recharge(self, amount):
        """
        从绑定的银行卡中扣款充值余额

        :param amount: 充值金额, 单位为元
        :type amount: float or int
        :return: 充值结果
        :rtype: dict

        >>> card.recharge(10)
        {'success': True, 'code': 0, 'msg': '转账成功'}
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
        info = self.get_json(self.URLs.RECHARGE, 'post', data)
        info = json.loads(info['Msg'])['transfer']
        result = {
            'code': int(info['retcode']),
            'msg': info['errmsg'],
            'success': not bool(int(info['retcode']))
        }
        return result

    @login_required
    def recharge_net(self, amount):
        """
        充值网费（一卡通余额 ==> 城市热点）

        :param amount: 充值金额, 单位为元
        :type amount: float or int
        :return: 充值结果

        >>> card.recharge_net(11)
        {'success': True, 'code' : 0, 'Msg' : '充值成功'}
        """
        data = {
            'paytype': 1,
            'aid': AIDS['net'],
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
        result = self.get_json(url=self.URLs.NET_PAY, method='post', data=data)
        result = json.loads(result['Msg'])
        return {
            'success': not int(result['pay_net_gdc']['retcode']),
            'code': int(result['pay_net_gdc']['retcode']),
            'msg': result['pay_net_gdc']['errmsg']
        }

    def _get_build_ids(self, aid):
        """获取建筑的id"""
        data = {
            'jsondata': '{"query_elec_building": {"aid": "%s", "account": "%s", "area": {"area": "", "areaname": ""}}}'
                        % (aid, self._get_inner_account()),
            'funname': 'synjones.onecard.query.elec.building',
            'json': True,
        }
        result = self.get_json(data=data, url=self.URLs.COMMON, method='post')
        result = json.loads(result['Msg'])
        # - -!
        building_id = {}
        for build in result['query_elec_building']['buildingtab']:
            building_id[build['building']] = build['buildingid']
        return building_id

    @login_required
    def recharge_xianlin_elec(self, amount, building_name, big_room_id, small_room_id=0):
        """
        充值仙林校区的寝室电费

        :param float amount: 充值金额
        :param str building_name: 楼栋名称，例如 "兰苑11栋"
        :param big_room_id: 大寝寝室号
        :type big_room_id: int or str
        :param small_room_id: 小寝寝室号， 不传或传0则表示充值为大寝电费， 1、2、3则充值对应小寝空调电费
        :type small_room_id: int or str
        :return: 充值结果
        :raise: :class:`njupt.exceptions.NjuptException` 楼栋名称不正确

        >>> card.recharge_xianlin_elec(
        >>>    amount=11,
        >>>    building_name='兰苑11栋',
        >>>    big_room_id=403,
        >>>    small_room_id=1
        >>> )
        {'code': 0, 'msg': '缴费成功！', 'success': True}
        """
        try:
            buiding_id = self._get_build_ids(AIDS['elec_xianlin'])[building_name]
            return self._recharge_electricity(amount=amount, elec_aid=AIDS['elec_xianlin'], building_id=buiding_id,
                                              building=building_name, room_id='{}{}'.format(big_room_id, small_room_id))
        except KeyError:
            raise NjuptException("不存在的楼栋")

    @login_required
    def recharge_sanpailou_elec(self, amount, building_name, room_id):
        """
        充值三牌楼校区的寝室电费，参数参考仙林校区（未测试
        """
        try:
            buiding_id = self._get_build_ids(AIDS['elec_sanpailou'])[building_name]
            return self._recharge_electricity(amount=amount, elec_aid=AIDS['elec_sanpailou'], building_id=buiding_id,
                                              building=building_name, room_id=room_id)
        except KeyError:
            raise NjuptException("不存在的楼栋")

    def _recharge_electricity(self, amount, elec_aid, building_id, building, room_id):
        data = {
            "acctype": "###",
            "paytype": 1,
            "aid": elec_aid,
            "account": self._get_inner_account(),
            "tran": int(amount * 100),
            "roomid": room_id,
            "room": "",
            "floorid": "",
            "floor": "",
            "buildingid": building_id,
            "building": building,
            "areaid": "",
            "areaname": "",
            "json": True
        }

        r = json.loads(self.get_json(self.URLs.ELEC_PAY, 'post', data=data)['Msg'])
        return {
            'success': not bool(int(r['pay_elec_gdc']['retcode'])),
            'code': int(r['pay_elec_gdc']['retcode']),
            'msg': r['pay_elec_gdc']['errmsg'],
        }

    @login_required
    def get_bill(self, start_date=(datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                 end_date=datetime.datetime.now().strftime("%Y-%m-%d"), rows=100, page=1):
        """
        查询一卡通消费记录，默认为最近一个月的消费记录

        :param start_date: 如 "2017-12-27"
        :param end_date:  如 "2018-01-26"
        :param rows: 一次查询返回的最大记录数量,默认为100条记录
        :param page: 如果结果数量有多页，决定返回第几页。
        :return: 查询到的信息，格式见例子
        :rtype: dict

        >>> card.get_bill()
        {
            'recodes':
                [
                    {
                        'balance': 39.71,
                        'change': -5,
                        'comment': '未知系统,交电费',
                        'department': '仙林售电处',
                        'time': '2018-01-26 20:55:40',
                        'type': '代扣代缴',
                        'week': '星期五'
                    },
                    ...
                ],
            'total': 52
            'total_pages': 2
            'page': 1
        }
        """
        data = {
            "sdate": start_date,
            "edate": end_date,
            "account": self._get_inner_account(),
            "page": page,
            "rows": rows
        }
        temp = self.get_json(url=self.URLs.BILL, method="post", data=data)
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
