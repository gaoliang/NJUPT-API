import pytest

from njupt.exceptions import NjuptException


def test_balance(card):
    assert card.get_balance()['total'] >= 0


def test_bill(card):
    assert 'recodes' in card.get_bill()


def test_net(card):
    assert card.get_net_balance() >= 0


def test_recharge(card):
    assert card.recharge_xianlin_elec(0.01, '兰苑11栋', '4031')['success']
    with pytest.raises(NjuptException):
        card.recharge_xianlin_elec(amount=0.01, building_name='不存在的', room_id=4031)
