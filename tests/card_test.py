import pytest
import pytz
from datetime import datetime

from njupt.exceptions import NjuptException

tz  = pytz.timezone('Asia/Shanghai')

def test_balance(card):
    assert card.get_balance()['total'] >= 0


def test_bill(card):
    assert 'recodes' in card.get_bill()


def test_net(card):
    assert card.get_net_balance() >= 0

def test_recharge(card):
    now = datetime.now(tz)
    if now.hour >= 23 or now.hour <= 6:
        assert not card.recharge(amount=0.01)['success']
    else:
        assert card.recharge(amount=0.01)['success']

def test_recharge_elec(card):
    with pytest.raises(NjuptException):
        card.recharge_xianlin_elec(amount=0.01, building_name='不存在的', room_id=4031)
    now = datetime.now(tz)
    if now.hour >= 23 or now.hour <= 6:
        assert not card.recharge_xianlin_elec(0.01, '兰苑11栋', '4031')['success']
    else:
        assert card.recharge_xianlin_elec(0.01, '兰苑11栋', '4031')['success']