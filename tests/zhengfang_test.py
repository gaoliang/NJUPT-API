import os
import unittest

from njupt.exceptions import UnauthorizedError, AuthenticationException
from njupt.models.zhengfang import Zhengfang

ACCOUNT = os.environ['ZHENGFANG_ACCOUNT']
RIGHT_PASSWORD = os.environ['ZHENGFANG_RIGHT_PASSWORD']
WRONG_PASSWORD = "wrong_password¬"


class ZhengfangTestCase(unittest.TestCase):
    """
    test zhengfang， need define account right password and wrong password before test
    """

    def test_not_login(self):
        zhengfang = Zhengfang()
        self.assertRaises(UnauthorizedError, zhengfang.get_score)

    def test_login(self):
        zhengfang = Zhengfang()
        self.assertEqual(0, zhengfang.login(ACCOUNT, RIGHT_PASSWORD)['code'])
        self.assertTrue(zhengfang.login(ACCOUNT, RIGHT_PASSWORD)['success'])
        self.assertRaises(AuthenticationException, zhengfang.login, ACCOUNT, WRONG_PASSWORD)

    def test_get_score(self):
        zhengfang = Zhengfang()
        zhengfang.login(ACCOUNT, RIGHT_PASSWORD)
        self.assertIn('gpa', zhengfang.get_score())

    def test_get_schedule(self):
        zhengfang = Zhengfang()
        zhengfang.login(ACCOUNT, RIGHT_PASSWORD)
        self.assertIsNot(zhengfang.get_schedule(1), [[None for col in range(13)] for row in range(8)])

    def test_get_courses(self):
        zhengfang = Zhengfang(ACCOUNT, RIGHT_PASSWORD)
        zhengfang.get_courses()
