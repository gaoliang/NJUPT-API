import os
import unittest

from njupt.exceptions import AuthenticationException, UnauthorizedError, NjuptException
from njupt.models.card import Card

CARD_ACCOUNT = os.environ['CARD_ACCOUNT']
CARD_RIGHT_PASSWORD = os.environ['CARD_RIGHT_PASSWORD']
CARD_WRONG_PASSWORD = "wrong_password¬"


class CardTestCase(unittest.TestCase):
    """
    test card， need define account right password and wrong password before test
    """

    def test_not_login(self):
        card = Card()
        self.assertRaises(UnauthorizedError, card.get_balance)

    def test_login(self):
        card = Card()
        self.assertEqual(0, card.login(CARD_ACCOUNT, CARD_RIGHT_PASSWORD)['code'])
        self.assertTrue(card.login(CARD_ACCOUNT, CARD_RIGHT_PASSWORD)['success'])
        self.assertRaises(AuthenticationException, card.login, CARD_ACCOUNT, CARD_WRONG_PASSWORD)

    def test_balance(self):
        card = Card()
        card.login(CARD_ACCOUNT, CARD_RIGHT_PASSWORD)
        self.assertGreaterEqual(card.get_balance()['total'], 0)

    def test_bill(self):
        card = Card(account=CARD_ACCOUNT, password=CARD_RIGHT_PASSWORD)
        self.assertIn('recodes', card.get_bill())

    def test_net(self):
        card = Card(account=CARD_ACCOUNT, password=CARD_RIGHT_PASSWORD)
        self.assertGreaterEqual(card.get_net_balance(), 0)

    def test_recharge(self):
        card = Card(account=CARD_ACCOUNT, password=CARD_RIGHT_PASSWORD)
        self.assertTrue(card.recharge_xianlin_elec(0.01, '兰苑11栋', '4031')['success'])
        self.assertRaises(NjuptException, card.recharge_xianlin_elec, 0.01, '稀奇古怪栋', '4031')
        self.assertFalse(card.recharge_xianlin_elec(-0.01, '兰苑11栋', '4031')['success'])
