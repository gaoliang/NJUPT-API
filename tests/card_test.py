import unittest
from pprint import pprint

from njupt.error import NjuptError, CardNotLogin
from njupt.models.card import Card
from tests.account_for_test import card_account, card_right_password, card_wrong_password


class CardTestCase(unittest.TestCase):
    """
    test card， need define account right password and wrong password before test
    """

    def test_not_login(self):
        card = Card()
        self.assertRaises(CardNotLogin, card.get_balance)

    def test_login(self):
        card = Card()
        self.assertEqual(0, card.login(card_account, card_right_password)['code'])
        self.assertEqual(1, card.login(card_account, card_wrong_password)['code'])
        self.assertTrue(card.login(card_account, card_right_password)['success'])
        self.assertFalse(card.login(card_account, card_wrong_password)['success'])

    def test_balance(self):
        card = Card()
        card.login(card_account, card_right_password)
        self.assertGreaterEqual(card.get_balance()['total'], 0)

    def test_bill(self):
        card = Card(account=card_account, password=card_right_password)
        self.assertIn('recodes', card.get_bill())

    def test_net(self):
        card = Card(account=card_account, password=card_right_password)
        self.assertGreaterEqual(card.get_net_balance(), 0)

    def test_recharge(self):
        card = Card(account=card_account, password=card_right_password)
        self.assertTrue(card.recharge_xianlin_elec(0.01, '兰苑11栋', '4031')['success'])
        self.assertRaises(NjuptError, card.recharge_xianlin_elec, 0.01, '稀奇古怪栋', '4031')
        self.assertFalse(card.recharge_xianlin_elec(-0.01, '兰苑11栋', '4031')['success'])
