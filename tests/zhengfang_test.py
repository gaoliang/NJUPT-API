import unittest

from njupt.exceptions import UnauthorizedError, AuthenticationException
from njupt.models.zhengfang import Zhengfang
from tests.account_for_test import account, right_password, wrong_password


class ZhengfangTestCase(unittest.TestCase):
    """
    test zhengfang， need define account right password and wrong password before test
    """

    def test_not_login(self):
        zhengfang = Zhengfang()
        self.assertRaises(UnauthorizedError, zhengfang.get_score)

    def test_login(self):
        zhengfang = Zhengfang()
        self.assertEqual(0, zhengfang.login(account, right_password)['code'])
        self.assertTrue(zhengfang.login(account, right_password)['success'])
        self.assertRaises(AuthenticationException, zhengfang.login, account, wrong_password)

    def test_get_score(self):
        zhengfang = Zhengfang()
        zhengfang.login(account, right_password)
        self.assertIn('gpa', zhengfang.get_score())

    def test_get_schedule(self):
        zhengfang = Zhengfang()
        zhengfang.login(account, right_password)
        self.assertIsNot(zhengfang.get_schedule(1), [[None for col in range(13)] for row in range(8)])

    def test_get_coursers(self):
        zhengfang = Zhengfang(account, right_password)
        zhengfang.get_coursers()
